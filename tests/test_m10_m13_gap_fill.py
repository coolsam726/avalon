"""Coverage fill for M10–M13 gap surfaces."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from avalon.filesystem.drivers.local import LocalAdapter
from avalon.filesystem.drivers.memory import MemoryAdapter
from avalon.filesystem.manager import Storage, StorageManager
from avalon.mail.markdown import render_content, render_markdown_component
from avalon.mail.mailable import Content
from avalon.notifications.notifiable import Notifiable
from avalon.notifications.notification import Notification, ShouldQueue
from avalon.notifications.sender import NotificationSender
from avalon.queue.failed import FailedJobRepository, report_failure
from avalon.queue.helpers import default_queue_config, get_dispatcher, get_manager, set_dispatcher, set_manager
from avalon.queue.job import Job, JobMiddleware


def test_local_write_and_read_stream(tmp_path: Path) -> None:
    disk = LocalAdapter(tmp_path)
    source = BytesIO(b"chunked-bytes")
    path = disk.write_stream("big.bin", source)
    assert path == "big.bin"
    with disk.read_stream("big.bin") as handle:
        assert handle.read() == b"chunked-bytes"
    disk.set_visibility("big.bin", "public")
    assert disk.get_visibility("big.bin") == "public"


def test_disk_write_stream_facade(tmp_path: Path) -> None:
    manager = StorageManager(
        config={"default": "local", "disks": {"local": {"driver": "local", "root": str(tmp_path)}}}
    )
    Storage.set_manager(manager)
    Storage.disk().write_stream("x.bin", BytesIO(b"abc"))
    assert Storage.get("x.bin") == b"abc"
    Storage.set_manager(None)


def test_memory_directory_ops() -> None:
    disk = MemoryAdapter()
    disk.make_directory("a/b")
    disk.put("a/b/c.txt", "hi")
    assert "a/b/c.txt" in disk.files("a", recursive=True)
    assert disk.directories("a")
    disk.delete_directory("a")
    assert not disk.exists("a/b/c.txt")


def test_markdown_component_and_theme_wrap() -> None:
    html = render_markdown_component("# Hello\n\n**Bold**\n\n[Go](https://example.com)")
    assert "<h1>" in html and "<strong>" in html and "button" in html
    body, text = render_content(
        Content(markdown=None, html="<p>Hi</p>", with_data={"app_name": "X"})
    )
    assert body == "<p>Hi</p>"
    assert text == "Hi"


@pytest.mark.asyncio
async def test_notification_should_queue_dispatches() -> None:
    from avalon.notifications.channels import ArrayChannel
    from avalon.queue.helpers import set_dispatcher, set_manager
    from avalon.queue.manager import QueueManager
    from avalon.queue.dispatcher import Dispatcher

    set_manager(QueueManager(config={"default": "sync", "connections": {"sync": {"driver": "sync"}}}))
    set_dispatcher(Dispatcher(get_manager()))

    class QueuedNote(ShouldQueue, Notification):
        def via(self, notifiable):
            return ["array"]

        def to_array(self, notifiable):
            return {"ok": True}

    class User(Notifiable):
        email = "a@b.c"

        def get_key(self):
            return 1

    ArrayChannel.clear()
    await NotificationSender().send(User(), QueuedNote())
    assert ArrayChannel.messages
    set_dispatcher(None)
    set_manager(None)


@pytest.mark.asyncio
async def test_report_failure_without_handler() -> None:
    class Boom(Job):
        def handle(self) -> None:
            raise RuntimeError("x")

    await report_failure(None, RuntimeError("x"), Boom())


def test_queue_helpers_defaults() -> None:
    set_dispatcher(None)
    set_manager(None)
    assert get_dispatcher() is not None
    assert get_manager() is not None
    cfg = default_queue_config()
    assert "sync" in cfg["connections"]


@pytest.mark.asyncio
async def test_job_middleware_passthrough() -> None:
    mw = JobMiddleware()

    async def nxt(job):
        return "ok"

    assert await mw.handle(Job(), nxt) == "ok"
