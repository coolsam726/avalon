"""Avalon filesystem — FlySystem-shaped Storage façade."""

from __future__ import annotations

from avalon.filesystem.helpers import storage
from avalon.filesystem.manager import Storage, StorageManager
from avalon.filesystem.storage import Disk

__all__ = ["Disk", "Storage", "StorageManager", "storage"]
