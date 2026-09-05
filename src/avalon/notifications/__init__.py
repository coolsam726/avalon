"""Avalon notifications — Notifiable, channels, database notifications."""

from __future__ import annotations

from avalon.notifications.channels import (
    ArrayChannel,
    DatabaseChannel,
    LogChannel,
    MailChannel,
)
from avalon.notifications.helpers import default_notifications_config, notify, notify_now
from avalon.notifications.messages import ResetPasswordNotification, VerifyEmailNotification
from avalon.notifications.notifiable import Notifiable
from avalon.notifications.notification import Notification, ShouldQueue
from avalon.notifications.schema import ensure_tables
from avalon.notifications.verification import (
    MustVerifyEmail,
    hash_email,
    mark_verified_from_request,
    verify_signature,
)

__all__ = [
    "ArrayChannel",
    "DatabaseChannel",
    "LogChannel",
    "MailChannel",
    "MustVerifyEmail",
    "Notifiable",
    "Notification",
    "ResetPasswordNotification",
    "ShouldQueue",
    "VerifyEmailNotification",
    "default_notifications_config",
    "ensure_tables",
    "hash_email",
    "mark_verified_from_request",
    "notify",
    "notify_now",
    "verify_signature",
]
