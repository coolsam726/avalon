"""Queue worker — pop and process jobs."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

from avalon.queue.connections.database import DatabaseQueue
from avalon.queue.failed import FailedJobRepository, report_failure
from avalon.queue.job import Job, call_handle, run_through_middleware

if TYPE_CHECKING:
    from avalon.queue.manager import QueueManager


class Worker:
    """Processes queued jobs."""

    def __init__(self, manager: QueueManager) -> None:
        self.manager = manager
        self.app = manager.app

    async def run(
        self,
        connection_name: str | None = None,
        *,
        queue: str = "default",
        once: bool = False,
        sleep: float = 1.0,
        max_jobs: int | None = None,
    ) -> int:
        processed = 0
        name = connection_name or self.manager.get_default_connection()
        while True:
            did_work = await self.run_once(name, queue=queue)
            if did_work:
                processed += 1
                if once or (max_jobs is not None and processed >= max_jobs):
                    return processed
                continue
            if once or (max_jobs is not None and processed >= max_jobs):
                return processed
            await asyncio.sleep(sleep)

    async def run_once(self, connection_name: str, *, queue: str = "default") -> bool:
        connection = self.manager.connection(connection_name)
        if isinstance(connection, DatabaseQueue):
            record = await connection.pop(queue)
            if record is None:
                return False
            job = Job.deserialize(json.loads(record["payload"]))
            try:
                await self.process_job(
                    job,
                    connection_name=connection_name,
                    database_record=record,
                    database_connection=connection,
                )
            except Exception as exc:
                await self._handle_failure(
                    job,
                    exc,
                    connection_name=connection_name,
                    queue=queue,
                    record=record,
                    database_connection=connection,
                )
            return True

        return False

    async def process_job(
        self,
        job: Job,
        *,
        connection_name: str,
        database_record: dict[str, Any] | None = None,
        database_connection: DatabaseQueue | None = None,
    ) -> Any:
        async def execute(current: Job) -> Any:
            return await call_handle(current)

        timeout = getattr(job, "timeout", None)
        if timeout is None:
            timeout = job.__class__.timeout

        try:
            if timeout is not None and float(timeout) > 0:
                result = await asyncio.wait_for(
                    run_through_middleware(job, execute),
                    timeout=float(timeout),
                )
            else:
                result = await run_through_middleware(job, execute)
        except TimeoutError as exc:
            raise TimeoutError(
                f"Job {type(job).__name__} timed out after {timeout}s"
            ) from exc
        except Exception:
            raise
        else:
            if database_connection is not None and database_record is not None:
                await database_connection.delete(int(database_record["id"]))
            return result

    async def _handle_failure(
        self,
        job: Job,
        exc: Exception,
        *,
        connection_name: str,
        queue: str,
        record: dict[str, Any],
        database_connection: DatabaseQueue,
    ) -> None:
        attempts = int(record.get("attempts") or 0) + 1
        max_tries = int(getattr(job, "tries", None) or job.__class__.tries or 1)
        await report_failure(self.app, exc, job)

        if attempts >= max_tries:
            repo = FailedJobRepository(self.manager.failed_config())
            await repo.store(
                uuid=database_connection.new_failed_uuid(),
                connection=connection_name,
                queue=queue,
                payload=json.loads(record["payload"]),
                exception=exc,
            )
            try:
                await job.failed(exc)
            except Exception:
                pass
            await database_connection.delete(int(record["id"]))
            return

        delay = _backoff_delay(job, attempts)
        await database_connection.release(int(record["id"]), delay=delay)


def _backoff_delay(job: Job, attempts: int) -> int:
    backoff = getattr(job, "backoff", None)
    if backoff is None:
        backoff = job.__class__.backoff
    if isinstance(backoff, list):
        index = min(attempts - 1, len(backoff) - 1)
        return int(backoff[index])
    if isinstance(backoff, int):
        return backoff
    return 0
