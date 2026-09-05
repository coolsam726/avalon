"""Failed job commands — ``queue:failed`` and ``queue:retry``."""

from __future__ import annotations

import asyncio
import json

from avalon.console.command import Command
from avalon.queue.connections.database import DatabaseQueue
from avalon.queue.failed import FailedJobRepository
from avalon.queue.manager import QueueManager


class QueueFailedCommand(Command):
    signature = "queue:failed {--limit=10}"
    description = "List failed queue jobs"

    def handle(self) -> int:
        manager = self.app.make(QueueManager)
        repo = FailedJobRepository(manager.failed_config())
        limit = int(self.option("limit") or 10)
        rows = asyncio.run(repo.all(limit=limit))
        if not rows:
            self.info("No failed jobs.")
            return 0
        table_rows = []
        for row in rows:
            payload = json.loads(row.get("payload") or "{}")
            job_class = payload.get("class", "?")
            table_rows.append(
                [
                    row.get("id"),
                    row.get("connection"),
                    row.get("queue"),
                    job_class,
                    str(row.get("failed_at") or "")[:19],
                ]
            )
        self.table(["ID", "Connection", "Queue", "Job", "Failed At"], table_rows)
        return 0


class QueueRetryCommand(Command):
    signature = "queue:retry {id?} {--all}"
    description = "Retry a failed queue job"

    def handle(self) -> int:
        manager = self.app.make(QueueManager)
        try:
            connection = manager.connection("database")
        except KeyError:
            self.error("Retry requires a database queue connection.")
            return 1
        if not isinstance(connection, DatabaseQueue):
            self.error("Retry requires a database queue connection.")
            return 1

        retry_all = bool(self.option("all"))
        failed_id = self.argument("id")

        async def _retry() -> int:
            if retry_all:
                count = await connection.restore_all_failed()
                return count
            if failed_id is None:
                return -1
            restored = await connection.restore_failed(int(failed_id))
            return 1 if restored else 0

        result = asyncio.run(_retry())
        if result == -1:
            self.error("Provide a failed job id or use --all.")
            return 1
        if result == 0:
            self.warn("Failed job not found or could not be restored.")
            return 1
        self.success(f"Retried {result} failed job(s).")
        return 0
