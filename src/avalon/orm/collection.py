"""Eloquent-shaped collection returned from every multi-row read."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Any, Generic, TypeVar

T = TypeVar("T")


def _pluck_value(item: Any, key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    getter = getattr(item, "get_attribute", None)
    if callable(getter):
        return getter(key)
    return getattr(item, key, None)


class Collection(Generic[T]):
    """List-like wrapper with Eloquent's collection helpers."""

    __slots__ = ("_items",)

    def __init__(self, items: Iterable[T] | None = None) -> None:
        self._items: list[T] = list(items or [])

    # --- container protocol -------------------------------------------------

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: Any) -> Any:
        if isinstance(index, slice):
            return Collection(self._items[index])
        return self._items[index]

    def __bool__(self) -> bool:
        return bool(self._items)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Collection):
            return self._items == other._items
        if isinstance(other, list):
            return self._items == other
        return NotImplemented

    def __repr__(self) -> str:
        return f"Collection({self._items!r})"

    # --- access -------------------------------------------------------------

    def all(self) -> list[T]:
        return list(self._items)

    def first(self, default: Any = None) -> Any:
        return self._items[0] if self._items else default

    def last(self, default: Any = None) -> Any:
        return self._items[-1] if self._items else default

    def is_empty(self) -> bool:
        return not self._items

    def is_not_empty(self) -> bool:
        return bool(self._items)

    def count(self) -> int:
        return len(self._items)

    # --- transformation -----------------------------------------------------

    def map(self, callback: Callable[[T], Any]) -> Collection[Any]:
        return Collection(callback(item) for item in self._items)

    def filter(self, callback: Callable[[T], bool] | None = None) -> Collection[T]:
        if callback is None:
            return Collection(item for item in self._items if item)
        return Collection(item for item in self._items if callback(item))

    def reject(self, callback: Callable[[T], bool]) -> Collection[T]:
        return Collection(item for item in self._items if not callback(item))

    def where(self, key: str, value: Any) -> Collection[T]:
        return Collection(item for item in self._items if _pluck_value(item, key) == value)

    def where_in(self, key: str, values: Iterable[Any]) -> Collection[T]:
        allowed = list(values)
        return Collection(item for item in self._items if _pluck_value(item, key) in allowed)

    def first_where(self, key: str, value: Any, default: Any = None) -> Any:
        return self.where(key, value).first(default)

    def pluck(self, key: str, index_key: str | None = None) -> Any:
        if index_key is None:
            return Collection(_pluck_value(item, key) for item in self._items)
        return {_pluck_value(item, index_key): _pluck_value(item, key) for item in self._items}

    def unique(self, key: str | None = None) -> Collection[T]:
        seen: list[Any] = []
        result: list[T] = []
        for item in self._items:
            marker = _pluck_value(item, key) if key else item
            if marker not in seen:
                seen.append(marker)
                result.append(item)
        return Collection(result)

    def sort_by(self, key: str | Callable[[T], Any], reverse: bool = False) -> Collection[T]:
        keyfunc = key if callable(key) else (lambda item: _pluck_value(item, str(key)))
        return Collection(sorted(self._items, key=keyfunc, reverse=reverse))

    def sort_by_desc(self, key: str | Callable[[T], Any]) -> Collection[T]:
        return self.sort_by(key, reverse=True)

    def group_by(self, key: str | Callable[[T], Any]) -> dict[Any, Collection[T]]:
        keyfunc = key if callable(key) else (lambda item: _pluck_value(item, str(key)))
        grouped: dict[Any, list[T]] = {}
        for item in self._items:
            grouped.setdefault(keyfunc(item), []).append(item)
        return {marker: Collection(items) for marker, items in grouped.items()}

    def key_by(self, key: str | Callable[[T], Any]) -> dict[Any, T]:
        keyfunc = key if callable(key) else (lambda item: _pluck_value(item, str(key)))
        return {keyfunc(item): item for item in self._items}

    def chunk(self, size: int) -> Collection[Collection[T]]:
        if size <= 0:
            raise ValueError("Chunk size must be positive")
        return Collection(
            Collection(self._items[index : index + size])
            for index in range(0, len(self._items), size)
        )

    def take(self, count: int) -> Collection[T]:
        return Collection(self._items[:count] if count >= 0 else self._items[count:])

    def skip(self, count: int) -> Collection[T]:
        return Collection(self._items[count:])

    def each(self, callback: Callable[[T], Any]) -> Collection[T]:
        for item in self._items:
            callback(item)
        return self

    def contains(self, callback: Callable[[T], bool] | Any) -> bool:
        if callable(callback):
            return any(callback(item) for item in self._items)
        return callback in self._items

    def sum(self, key: str | None = None) -> Any:
        values = [_pluck_value(item, key) if key else item for item in self._items]
        return sum(value for value in values if value is not None)

    def avg(self, key: str | None = None) -> Any:
        values = [_pluck_value(item, key) if key else item for item in self._items]
        clean = [value for value in values if value is not None]
        return (sum(clean) / len(clean)) if clean else None

    def max(self, key: str | None = None) -> Any:
        values = [_pluck_value(item, key) if key else item for item in self._items]
        clean = [value for value in values if value is not None]
        return max(clean) if clean else None

    def min(self, key: str | None = None) -> Any:
        values = [_pluck_value(item, key) if key else item for item in self._items]
        clean = [value for value in values if value is not None]
        return min(clean) if clean else None

    def push(self, item: T) -> Collection[T]:
        self._items.append(item)
        return self

    def merge(self, items: Iterable[T]) -> Collection[T]:
        return Collection([*self._items, *items])

    def reverse(self) -> Collection[T]:
        return Collection(reversed(self._items))

    def values(self) -> Collection[T]:
        return Collection(self._items)

    # --- model helpers ------------------------------------------------------

    def model_keys(self) -> list[Any]:
        return [item.get_key() for item in self._items]  # type: ignore[attr-defined]

    def to_dict(self) -> list[Any]:
        result: list[Any] = []
        for item in self._items:
            serializer = getattr(item, "to_dict", None)
            result.append(serializer() if callable(serializer) else item)
        return result

    async def load(self, *relations: str) -> Collection[T]:
        """Lazy eager-load relations onto every model in the collection."""
        if not self._items:
            return self
        from avalon.orm.eager import eager_load

        await eager_load(list(self._items), relations)
        return self

    async def load_missing(self, *relations: str) -> Collection[T]:
        pending = [
            name
            for name in relations
            if any(not item.relation_loaded(name.split(".")[0]) for item in self._items)  # type: ignore[attr-defined]
        ]
        if pending:
            await self.load(*pending)
        return self
