"""Relationships — every Eloquent relation type."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa

from avalon.orm.builder import QueryBuilder, _MISSING
from avalon.orm.collection import Collection
from avalon.orm.inflector import pivot_table

if TYPE_CHECKING:
    from avalon.orm.model import Model

PIVOT_PARENT = "__pivot_parent"


class Relation:
    """Base relation: proxies the builder and knows how to eager load."""

    def __init__(self, parent: Model, related: type[Model]) -> None:
        self.parent = parent
        self.related = related

    # --- builder proxy ------------------------------------------------------

    def query(self) -> QueryBuilder:
        raise NotImplementedError

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self.query(), name)

    async def get(self) -> Collection[Any]:
        return await self.query().get()

    async def first(self) -> Any:
        return await self.query().first()

    async def count(self) -> int:
        return await self.query().count()

    async def exists(self) -> bool:
        return await self.query().exists()

    # --- eager loading contract --------------------------------------------

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        raise NotImplementedError

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        raise NotImplementedError

    def existence_query(
        self,
        parent_builder: QueryBuilder,
        callback: Callable[[QueryBuilder], Any] | None = None,
    ) -> Any:
        raise NotImplementedError

    def grouping_column(self) -> str:
        """Column `with_count` groups by to bucket rows per parent."""
        raise NotImplementedError

    def parent_match_key(self) -> str:
        """Parent attribute whose value matches `grouping_column`."""
        raise NotImplementedError

    # --- helpers ------------------------------------------------------------

    def _related_builder(self) -> QueryBuilder:
        return self.related.new_query()

    @staticmethod
    def _keys(models: Sequence[Model], key: str) -> list[Any]:
        seen: list[Any] = []
        for model in models:
            value = model.get_raw_attribute(key)
            if value is not None and value not in seen:
                seen.append(value)
        return seen


class HasOneOrMany(Relation):
    """Shared behaviour for `has_one` / `has_many`."""

    def __init__(
        self,
        parent: Model,
        related: type[Model],
        foreign_key: str,
        local_key: str,
    ) -> None:
        super().__init__(parent, related)
        self.foreign_key = foreign_key
        self.local_key = local_key

    def query(self) -> QueryBuilder:
        return self._related_builder().where(
            self.foreign_key, "=", self.parent.get_raw_attribute(self.local_key)
        )

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        keys = self._keys(models, self.local_key)
        return self._related_builder().where_in(self.foreign_key, keys)

    def _group(self, results: Collection[Any]) -> dict[Any, list[Any]]:
        grouped: dict[Any, list[Any]] = {}
        for item in results:
            grouped.setdefault(item.get_raw_attribute(self.foreign_key), []).append(item)
        return grouped

    def grouping_column(self) -> str:
        return f"{self.related.get_table()}.{self.foreign_key}"

    def parent_match_key(self) -> str:
        return self.local_key

    def existence_query(
        self,
        parent_builder: QueryBuilder,
        callback: Callable[[QueryBuilder], Any] | None = None,
    ) -> Any:
        builder = self._related_builder()
        builder._apply_global_scopes(builder)
        if callback is not None:
            callback(builder)
        outer = parent_builder.column(f"{self.parent.get_table()}.{self.local_key}")
        builder._push_where(
            "and", builder.column(f"{self.related.get_table()}.{self.foreign_key}") == outer
        )
        return builder._base_select([sa.literal(1)])

    async def create(self, attributes: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        payload = {
            **(attributes or {}),
            **kwargs,
            self.foreign_key: self.parent.get_raw_attribute(self.local_key),
        }
        instance = self.related()
        instance.force_fill(payload)
        await instance.save()
        return instance

    async def save(self, model: Model) -> Any:
        model.set_attribute(self.foreign_key, self.parent.get_raw_attribute(self.local_key))
        await model.save()
        return model

    async def save_many(self, models: Iterable[Model]) -> list[Any]:
        return [await self.save(model) for model in models]

    async def create_many(self, records: Iterable[Mapping[str, Any]]) -> list[Any]:
        return [await self.create(record) for record in records]

    async def first_or_create(
        self,
        attributes: Mapping[str, Any],
        values: Mapping[str, Any] | None = None,
    ) -> Any:
        probe = self.query()
        for key, value in attributes.items():
            probe.where(key, "=", value)
        found = await probe.first()
        if found is not None:
            return found
        return await self.create({**attributes, **(values or {})})


class HasMany(HasOneOrMany):
    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped = self._group(results)
        for model in models:
            key = model.get_raw_attribute(self.local_key)
            model.set_relation(name, Collection(grouped.get(key, [])))


class HasOne(HasOneOrMany):
    async def get(self) -> Any:  # type: ignore[override]
        return await self.query().first()

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped = self._group(results)
        for model in models:
            key = model.get_raw_attribute(self.local_key)
            matches = grouped.get(key, [])
            model.set_relation(name, matches[0] if matches else None)


class BelongsTo(Relation):
    def __init__(
        self,
        child: Model,
        related: type[Model],
        foreign_key: str,
        owner_key: str,
    ) -> None:
        super().__init__(child, related)
        self.foreign_key = foreign_key
        self.owner_key = owner_key

    def query(self) -> QueryBuilder:
        return self._related_builder().where(
            self.owner_key, "=", self.parent.get_raw_attribute(self.foreign_key)
        )

    async def get(self) -> Any:  # type: ignore[override]
        return await self.query().first()

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        keys = self._keys(models, self.foreign_key)
        return self._related_builder().where_in(self.owner_key, keys)

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        index = {item.get_raw_attribute(self.owner_key): item for item in results}
        for model in models:
            model.set_relation(name, index.get(model.get_raw_attribute(self.foreign_key)))

    def existence_query(
        self,
        parent_builder: QueryBuilder,
        callback: Callable[[QueryBuilder], Any] | None = None,
    ) -> Any:
        builder = self._related_builder()
        builder._apply_global_scopes(builder)
        if callback is not None:
            callback(builder)
        outer = parent_builder.column(f"{self.parent.get_table()}.{self.foreign_key}")
        builder._push_where(
            "and", builder.column(f"{self.related.get_table()}.{self.owner_key}") == outer
        )
        return builder._base_select([sa.literal(1)])

    def grouping_column(self) -> str:
        return f"{self.related.get_table()}.{self.owner_key}"

    def parent_match_key(self) -> str:
        return self.foreign_key

    def associate(self, model: Model | Any) -> Model:
        value = model.get_raw_attribute(self.owner_key) if hasattr(model, "get_raw_attribute") else model
        self.parent.set_attribute(self.foreign_key, value)
        return self.parent

    def dissociate(self) -> Model:
        self.parent.set_attribute(self.foreign_key, None)
        return self.parent


class BelongsToMany(Relation):
    """Many-to-many through a pivot table."""

    def __init__(
        self,
        parent: Model,
        related: type[Model],
        table: str | None = None,
        foreign_pivot_key: str | None = None,
        related_pivot_key: str | None = None,
    ) -> None:
        super().__init__(parent, related)
        self.pivot = table or pivot_table(type(parent).__name__, related.__name__)
        self.foreign_pivot_key = foreign_pivot_key or type(parent).get_foreign_key()
        self.related_pivot_key = related_pivot_key or related.get_foreign_key()
        self.parent_key = type(parent).primary_key
        self.related_key = related.primary_key
        self._pivot_columns: list[str] = []

    def with_pivot(self, *columns: str) -> BelongsToMany:
        self._pivot_columns.extend(columns)
        return self

    def _join(self, builder: QueryBuilder) -> QueryBuilder:
        related_table = self.related.get_table()
        builder.join(
            self.pivot,
            f"{self.pivot}.{self.related_pivot_key}",
            "=",
            f"{related_table}.{self.related_key}",
        )
        selects: list[Any] = [sa.literal_column(f"{related_table}.*")]
        for column in self._pivot_columns:
            selects.append(builder.column(f"{self.pivot}.{column}").label(f"pivot_{column}"))
        builder.select(*selects)
        return builder

    def query(self) -> QueryBuilder:
        builder = self._join(self._related_builder())
        return builder.where(
            f"{self.pivot}.{self.foreign_pivot_key}",
            "=",
            self.parent.get_raw_attribute(self.parent_key),
        )

    def where_pivot(
        self,
        column: str,
        operator: Any = _MISSING,
        value: Any = _MISSING,
    ) -> QueryBuilder:
        return self.query().where(f"{self.pivot}.{column}", operator, value)

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        keys = self._keys(models, self.parent_key)
        builder = self._join(self._related_builder())
        builder.add_select(
            builder.column(f"{self.pivot}.{self.foreign_pivot_key}").label(PIVOT_PARENT)
        )
        return builder.where_in(f"{self.pivot}.{self.foreign_pivot_key}", keys)

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped: dict[Any, list[Any]] = {}
        for item in results:
            marker = item.get_raw_attribute(PIVOT_PARENT)
            item._attributes.pop(PIVOT_PARENT, None)
            grouped.setdefault(marker, []).append(item)
        for model in models:
            key = model.get_raw_attribute(self.parent_key)
            model.set_relation(name, Collection(grouped.get(key, [])))

    def existence_query(
        self,
        parent_builder: QueryBuilder,
        callback: Callable[[QueryBuilder], Any] | None = None,
    ) -> Any:
        builder = self._join(self._related_builder())
        builder._apply_global_scopes(builder)
        if callback is not None:
            callback(builder)
        outer = parent_builder.column(f"{self.parent.get_table()}.{self.parent_key}")
        builder._push_where(
            "and", builder.column(f"{self.pivot}.{self.foreign_pivot_key}") == outer
        )
        builder._selects = []
        return builder._base_select([sa.literal(1)])

    def grouping_column(self) -> str:
        return f"{self.pivot}.{self.foreign_pivot_key}"

    def parent_match_key(self) -> str:
        return self.parent_key

    # --- pivot mutations ----------------------------------------------------

    def _pivot_query(self) -> QueryBuilder:
        return QueryBuilder.for_table(self.pivot, connection=self.related.connection)

    async def attach(
        self,
        ids: Any,
        attributes: Mapping[str, Any] | None = None,
    ) -> int:
        rows = []
        for identifier in _as_keys(ids):
            rows.append(
                {
                    self.foreign_pivot_key: self.parent.get_raw_attribute(self.parent_key),
                    self.related_pivot_key: identifier,
                    **(attributes or {}),
                }
            )
        if not rows:
            return 0
        return await self._pivot_query().insert(rows)

    async def detach(self, ids: Any = None) -> int:
        builder = self._pivot_query().where(
            self.foreign_pivot_key, "=", self.parent.get_raw_attribute(self.parent_key)
        )
        if ids is not None:
            builder.where_in(self.related_pivot_key, _as_keys(ids))
        return await builder.delete()

    async def sync(self, ids: Any, detaching: bool = True) -> dict[str, list[Any]]:
        desired = _as_keys(ids)
        current = await self.pivot_ids()
        attached = [key for key in desired if key not in current]
        detached = [key for key in current if key not in desired] if detaching else []

        if detached:
            await self.detach(detached)
        if attached:
            await self.attach(attached)
        return {"attached": attached, "detached": detached, "updated": []}

    async def toggle(self, ids: Any) -> dict[str, list[Any]]:
        requested = _as_keys(ids)
        current = await self.pivot_ids()
        attach = [key for key in requested if key not in current]
        detach = [key for key in requested if key in current]
        if detach:
            await self.detach(detach)
        if attach:
            await self.attach(attach)
        return {"attached": attach, "detached": detach}

    async def update_existing_pivot(self, identifier: Any, attributes: Mapping[str, Any]) -> int:
        return await (
            self._pivot_query()
            .where(self.foreign_pivot_key, "=", self.parent.get_raw_attribute(self.parent_key))
            .where(self.related_pivot_key, "=", identifier)
            .update(dict(attributes))
        )

    async def pivot_ids(self) -> list[Any]:
        rows = await (
            self._pivot_query()
            .where(self.foreign_pivot_key, "=", self.parent.get_raw_attribute(self.parent_key))
            .select(self.related_pivot_key)
            .get_raw()
        )
        return [row[self.related_pivot_key] for row in rows]


class HasManyThrough(Relation):
    """`Country -> has_many_through(Post, User)`."""

    def __init__(
        self,
        parent: Model,
        related: type[Model],
        through: type[Model],
        first_key: str | None = None,
        second_key: str | None = None,
    ) -> None:
        super().__init__(parent, related)
        self.through = through
        self.first_key = first_key or type(parent).get_foreign_key()
        self.second_key = second_key or through.get_foreign_key()
        self.local_key = type(parent).primary_key
        self.through_key = through.primary_key

    def _join(self, builder: QueryBuilder) -> QueryBuilder:
        through_table = self.through.get_table()
        related_table = self.related.get_table()
        builder.join(
            through_table,
            f"{through_table}.{self.through_key}",
            "=",
            f"{related_table}.{self.second_key}",
        )
        return builder

    def query(self) -> QueryBuilder:
        builder = self._join(self._related_builder())
        builder.select(sa.literal_column(f"{self.related.get_table()}.*"))
        return builder.where(
            f"{self.through.get_table()}.{self.first_key}",
            "=",
            self.parent.get_raw_attribute(self.local_key),
        )

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        keys = self._keys(models, self.local_key)
        through_table = self.through.get_table()
        builder = self._join(self._related_builder())
        builder.select(sa.literal_column(f"{self.related.get_table()}.*"))
        builder.add_select(
            builder.column(f"{through_table}.{self.first_key}").label(PIVOT_PARENT)
        )
        return builder.where_in(f"{through_table}.{self.first_key}", keys)

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped: dict[Any, list[Any]] = {}
        for item in results:
            marker = item.get_raw_attribute(PIVOT_PARENT)
            item._attributes.pop(PIVOT_PARENT, None)
            grouped.setdefault(marker, []).append(item)
        for model in models:
            key = model.get_raw_attribute(self.local_key)
            model.set_relation(name, Collection(grouped.get(key, [])))

    def existence_query(
        self,
        parent_builder: QueryBuilder,
        callback: Callable[[QueryBuilder], Any] | None = None,
    ) -> Any:
        builder = self._join(self._related_builder())
        builder._apply_global_scopes(builder)
        if callback is not None:
            callback(builder)
        outer = parent_builder.column(f"{self.parent.get_table()}.{self.local_key}")
        builder._push_where(
            "and",
            builder.column(f"{self.through.get_table()}.{self.first_key}") == outer,
        )
        builder._selects = []
        return builder._base_select([sa.literal(1)])

    def grouping_column(self) -> str:
        return f"{self.through.get_table()}.{self.first_key}"

    def parent_match_key(self) -> str:
        return self.local_key


class HasOneThrough(HasManyThrough):
    async def get(self) -> Any:  # type: ignore[override]
        return await self.query().first()

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped: dict[Any, list[Any]] = {}
        for item in results:
            marker = item.get_raw_attribute(PIVOT_PARENT)
            item._attributes.pop(PIVOT_PARENT, None)
            grouped.setdefault(marker, []).append(item)
        for model in models:
            key = model.get_raw_attribute(self.local_key)
            matches = grouped.get(key, [])
            model.set_relation(name, matches[0] if matches else None)


class MorphOneOrMany(HasOneOrMany):
    """Polymorphic child relation keyed by `{name}_id` / `{name}_type`."""

    def __init__(self, parent: Model, related: type[Model], name: str) -> None:
        super().__init__(parent, related, f"{name}_id", type(parent).primary_key)
        self.morph_name = name
        self.morph_type = f"{name}_type"
        self.morph_class = type(parent).__name__

    def query(self) -> QueryBuilder:
        return super().query().where(self.morph_type, "=", self.morph_class)

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        return super().eager_query(models).where(self.morph_type, "=", self.morph_class)

    def existence_query(
        self,
        parent_builder: QueryBuilder,
        callback: Callable[[QueryBuilder], Any] | None = None,
    ) -> Any:
        def constrained(builder: QueryBuilder) -> None:
            builder.where(f"{self.related.get_table()}.{self.morph_type}", "=", self.morph_class)
            if callback is not None:
                callback(builder)

        return super().existence_query(parent_builder, constrained)

    async def create(self, attributes: Mapping[str, Any] | None = None, **kwargs: Any) -> Any:
        payload = {**(attributes or {}), **kwargs, self.morph_type: self.morph_class}
        return await super().create(payload)


class MorphMany(MorphOneOrMany):
    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped = self._group(results)
        for model in models:
            key = model.get_raw_attribute(self.local_key)
            model.set_relation(name, Collection(grouped.get(key, [])))


class MorphOne(MorphOneOrMany):
    async def get(self) -> Any:  # type: ignore[override]
        return await self.query().first()

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        grouped = self._group(results)
        for model in models:
            matches = grouped.get(model.get_raw_attribute(self.local_key), [])
            model.set_relation(name, matches[0] if matches else None)


class MorphTo(Relation):
    """Inverse polymorphic relation — resolves `{name}_type` to a model."""

    def __init__(self, child: Model, name: str, types: Mapping[str, type[Model]]) -> None:
        super().__init__(child, type(child))
        self.morph_name = name
        self.morph_id = f"{name}_id"
        self.morph_type = f"{name}_type"
        self.types = dict(types)

    def _target(self, alias: str | None) -> type[Model] | None:
        return self.types.get(str(alias)) if alias else None

    def query(self) -> QueryBuilder:
        target = self._target(self.parent.get_raw_attribute(self.morph_type))
        if target is None:
            raise LookupError(
                f"Unmapped morph type "
                f"{self.parent.get_raw_attribute(self.morph_type)!r} for {self.morph_name!r}"
            )
        return target.new_query().where(
            target.primary_key, "=", self.parent.get_raw_attribute(self.morph_id)
        )

    async def get(self) -> Any:  # type: ignore[override]
        if self.parent.get_raw_attribute(self.morph_id) is None:
            return None
        return await self.query().first()

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:  # pragma: no cover
        raise NotImplementedError("morph_to eager loading uses eager_load_morph_to")

    def match(self, models: Sequence[Model], results: Collection[Any], name: str) -> None:
        raise NotImplementedError  # pragma: no cover

    async def eager_load_into(self, models: Sequence[Model], name: str) -> None:
        buckets: dict[str, list[Model]] = {}
        for model in models:
            alias = model.get_raw_attribute(self.morph_type)
            if alias:
                buckets.setdefault(str(alias), []).append(model)

        for alias, group in buckets.items():
            target = self._target(alias)
            if target is None:
                for model in group:
                    model.set_relation(name, None)
                continue
            keys = [model.get_raw_attribute(self.morph_id) for model in group]
            found = await target.new_query().where_in(target.primary_key, keys).get()
            index = {item.get_raw_attribute(target.primary_key): item for item in found}
            for model in group:
                model.set_relation(name, index.get(model.get_raw_attribute(self.morph_id)))


class MorphToMany(BelongsToMany):
    """Polymorphic many-to-many (`taggables`-style pivot)."""

    def __init__(
        self,
        parent: Model,
        related: type[Model],
        name: str,
        table: str | None = None,
        inverse: bool = False,
    ) -> None:
        pivot = table or f"{name}s"
        morph_owner = related if inverse else type(parent)
        other = type(parent) if inverse else related
        super().__init__(
            parent,
            related,
            table=pivot,
            foreign_pivot_key=f"{name}_id" if not inverse else other.get_foreign_key(),
            related_pivot_key=related.get_foreign_key() if not inverse else f"{name}_id",
        )
        self.morph_name = name
        self.morph_type = f"{name}_type"
        self.inverse = inverse
        self.morph_class = morph_owner.__name__ if inverse else type(parent).__name__

    def query(self) -> QueryBuilder:
        return super().query().where(f"{self.pivot}.{self.morph_type}", "=", self.morph_class)

    def eager_query(self, models: Sequence[Model]) -> QueryBuilder:
        return (
            super()
            .eager_query(models)
            .where(f"{self.pivot}.{self.morph_type}", "=", self.morph_class)
        )

    async def attach(self, ids: Any, attributes: Mapping[str, Any] | None = None) -> int:
        return await super().attach(ids, {**(attributes or {}), self.morph_type: self.morph_class})

    async def detach(self, ids: Any = None) -> int:
        builder = (
            self._pivot_query()
            .where(self.foreign_pivot_key, "=", self.parent.get_raw_attribute(self.parent_key))
            .where(self.morph_type, "=", self.morph_class)
        )
        if ids is not None:
            builder.where_in(self.related_pivot_key, _as_keys(ids))
        return await builder.delete()


def _as_keys(ids: Any) -> list[Any]:
    if isinstance(ids, (list, tuple, set)):
        return [_key_of(item) for item in ids]
    return [_key_of(ids)]


def _key_of(value: Any) -> Any:
    getter = getattr(value, "get_key", None)
    return getter() if callable(getter) else value


__all__ = [
    "BelongsTo",
    "BelongsToMany",
    "HasMany",
    "HasManyThrough",
    "HasOne",
    "HasOneThrough",
    "MorphMany",
    "MorphOne",
    "MorphTo",
    "MorphToMany",
    "Relation",
]
