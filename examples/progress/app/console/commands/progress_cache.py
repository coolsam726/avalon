"""Demo Cache façade in the living example."""

from __future__ import annotations

from avalon.cache import Cache
from avalon.console.command import Command


class ProgressCacheCommand(Command):
    signature = "progress:cache"
    description = "Demo Cache get/put/remember/lock (M15)"

    def handle(self) -> int:
        Cache.put("progress:hello", "avalon", 60)
        self.info(f"get → {Cache.get('progress:hello')}")
        value = Cache.remember("progress:answer", 60, lambda: 42)
        self.info(f"remember → {value}")
        with Cache.lock("progress:demo", seconds=10):
            self.line("lock acquired")
        Cache.forget("progress:hello")
        self.success("cache demo ok")
        return 0
