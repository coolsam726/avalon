"""Eloquent-shaped collection — Support Collection + model helpers."""

from __future__ import annotations

from typing import Any, TypeVar

from avalon.support.collection import Collection as SupportCollection

T = TypeVar("T")


class Collection(SupportCollection[T]):
    """Model collection returned from multi-row Articulate reads."""

    def model_keys(self) -> list[Any]:
        return [item.get_key() for item in self]  # type: ignore[attr-defined]

    def to_dict(self) -> list[Any]:
        result: list[Any] = []
        for item in self:
            serializer = getattr(item, "to_dict", None)
            result.append(serializer() if callable(serializer) else item)
        return result

    async def load(self, *relations: str) -> Collection[T]:
        """Lazy eager-load relations onto every model in the collection."""
        items = self._values_list()
        if not items:
            return self
        from avalon.orm.eager import eager_load

        await eager_load(items, relations)
        return self

    async def load_missing(self, *relations: str) -> Collection[T]:
        items = self._values_list()
        pending = [
            name
            for name in relations
            if any(not item.relation_loaded(name.split(".")[0]) for item in items)  # type: ignore[attr-defined]
        ]
        if pending:
            await self.load(*pending)
        return self
