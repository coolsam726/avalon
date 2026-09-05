"""Avalon mail — Mailable, Mailer, transports."""

from __future__ import annotations

from avalon.mail.helpers import Mail, mail
from avalon.mail.mailable import (
    Address,
    Attachment,
    Content,
    Envelope,
    Mailable,
    ShouldQueue,
)
from avalon.mail.mailer import MailManager, Mailer, PendingMail
from avalon.mail.message import SentMessage
from avalon.mail.testing import MailAssertions

__all__ = [
    "Address",
    "Attachment",
    "Content",
    "Envelope",
    "Mail",
    "MailAssertions",
    "MailManager",
    "Mailer",
    "Mailable",
    "PendingMail",
    "SentMessage",
    "ShouldQueue",
    "mail",
]
