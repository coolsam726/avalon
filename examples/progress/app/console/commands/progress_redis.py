"""Demo Redis façade — skips cleanly when Redis is unreachable."""

from __future__ import annotations

from avalon.console.command import Command


class ProgressRedisCommand(Command):
    signature = "progress:redis"
    description = "Demo Redis façade / cache store (M16); skips if Redis is down"

    def handle(self) -> int:
        try:
            from avalon.redis import Redis, require_redis

            require_redis()
            Redis.set("progress:redis:ping", b"pong", ex=30)
            value = Redis.get("progress:redis:ping")
            self.info(f"Redis.get → {value!r}")
            Redis.delete("progress:redis:ping")

            from avalon.cache import Cache

            Cache.store("redis").put("progress:redis:cache", "ok", 30)
            cached = Cache.store("redis").get("progress:redis:cache")
            self.info(f"Cache.store('redis') → {cached!r}")
            Cache.store("redis").forget("progress:redis:cache")
        except Exception as exc:
            self.warn(f"Redis unavailable ({exc}); skipping live demo")
            self.comment("Install redis + avalon[redis], start a server, then retry.")
            return 0

        self.success("redis demo ok")
        return 0
