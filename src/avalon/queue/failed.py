"""Failed job repository."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from avalon.queue.job import Job


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class FailedJobRepository:
    """Persists exhausted jobs."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = dict(config or {})
        self.table = str(self.config.get("table") or "failed_jobs")
        self.db_connection = str(self.config.get("connection") or "default")

    async def store(
        self,
        *,
        uuid: str,
        connection: str,
        queue: str,
        payload: dict[str, Any],
        exception: BaseException,
    ) -> None:
        from avalon.orm.facade import DB

        await DB.statement(
            f"""
            INSERT INTO {self.table}
                (uuid, connection, queue, payload, exception, failed_at)
            VALUES
                (:uuid, :connection, :queue, :payload, :exception, :failed_at)
            """,
            {
                "uuid": uuid,
                "connection": connection,
                "queue": queue,
                "payload": json.dumps(payload),
                "exception": _format_exception(exception),
                "failed_at": _utcnow(),
            },
            connection=self.db_connection,
        )

    async def all(self, *, limit: int | None = None) -> list[dict[str, Any]]:
        from avalon.orm.facade import DB

        sql = f"SELECT id, uuid, connection, queue, payload, exception, failed_at FROM {self.table} ORDER BY id DESC"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return await DB.select(sql, connection=self.db_connection)

    async def find(self, failed_id: int) -> dict[str, Any] | None:
        from avalon.orm.facade import DB

        return await DB.select_one(
            f"SELECT id, uuid, connection, queue, payload, exception, failed_at FROM {self.table} WHERE id = :id",
            {"id": failed_id},
            connection=self.db_connection,
        )

    async def delete(self, failed_id: int) -> None:
        from avalon.orm.facade import DB

        await DB.statement(
            f"DELETE FROM {self.table} WHERE id = :id",
            {"id": failed_id},
            connection=self.db_connection,
        )

    async def flush(self) -> int:
        from avalon.orm.facade import DB

        result = await DB.statement(f"DELETE FROM {self.table}", connection=self.db_connection)
        return int(result)


async def report_failure(app: Any | None, exc: BaseException, job: Job) -> None:
    """Report through M8 Handler when available."""
    if app is None:
        return
    try:
        from avalon.exceptions.handler import Handler

        if app.container.bound(Handler):
            handler = app.make(Handler)
        else:
            handler = Handler(app)
        handler.report(exc)
    except Exception:
        pass


def _format_exception(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"
