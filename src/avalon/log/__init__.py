"""Application logging — channels and ``log()`` helper (M8)."""

from __future__ import annotations

from avalon.log.helpers import log
from avalon.log.manager import LogManager, get_logger

__all__ = ["LogManager", "get_logger", "log"]
