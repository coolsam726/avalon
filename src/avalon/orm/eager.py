"""Eager loading — the cure for N+1, shipped with the relations."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

import sqlalchemy as sa

from avalon.orm.builder import QueryBuilder
from avalon.orm.collection import Collection
from avalon.orm.relations import MorphTo, Relation


def _normalize(relations: Any) -> dict[str, Callable[[QueryBuilder], Any] | None]:
    """Accept `("a", "b.c")`, `{"a": callback}`, or a mix."""
    normalized: dict[str, Callable[[QueryBuilder], Any] | None] = {}
    if isinstance(relations, Mapping):
        for name, callback in relations.items():
            normalized[str(name)] = callback
        return normalized
    for item in relations:
        if isinstance(item, Mapping):
            normalized.update({str(k): v for k, v in item.items()})
        else:
            normalized.setdefault(str(item), None)
    return normalized


def _split(
    relations: dict[str, Callable[[QueryBuilder], Any] | None],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    top: dict[str, Any] = {}
    nested: dict[str, dict[str, Any]] = {}
    for name, callback in relations.items():
        head, _, tail = name.partition(".")
        if tail:
            top.setdefault(head, None)
            nested.setdefault(head, {})[tail] = callback
        else:
            # An explicit callback wins over a bare mention from a nested path.
            if callback is not None or head not in top:
                top[head] = callback
    return top, nested


def _children(models: Sequence[Any], name: str) -> list[Any]:
    collected: list[Any] = []
    for model in models:
        value = model.get_relations().get(name)
        if value is None:
            continue
        if isinstance(value, Collection):
            collected.extend(value)
        else:
            collected.append(value)
    return collected


async def eager_load(models: Sequence[Any], relations: Any) -> None:
    """Load `relations` onto `models` with one query per relation level."""
    if not models:
        return

    normalized = _normalize(relations)
    if not normalized:
        return
    top, nested = _split(normalized)

    for name, callback in top.items():
        relation = models[0].get_relation(name)

        if isinstance(relation, MorphTo):
            await relation.eager_load_into(models, name)
        else:
            builder = relation.eager_query(models)
            if callback is not None:
                callback(builder)
            results = await builder.get()
            relation.match(models, results, name)

        if name in nested:
            children = _children(models, name)
            if children:
                await eager_load(children, nested[name])


async def eager_load_counts(models: Sequence[Any], relation_name: str, alias: str) -> None:
    """Attach `{relation}_count` without hydrating the related rows."""
    if not models:
        return

    relation: Relation = models[0].get_relation(relation_name)
    grouping = relation.grouping_column()
    parent_key = relation.parent_match_key()

    builder = relation.eager_query(models)
    builder._selects = []
    builder._eager = {}
    builder._eager_counts = []
    column = builder.column(grouping)
    builder.select(column.label("__group"), sa.func.count().label("__count"))
    builder.group_by(column)

    rows = await builder.get_raw()
    counts = {row["__group"]: int(row["__count"]) for row in rows}

    for model in models:
        model._extra[alias] = counts.get(model.get_raw_attribute(parent_key), 0)
