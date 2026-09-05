"""Mail transports package."""

from __future__ import annotations

from avalon.mail.transports.array import ArrayTransport
from avalon.mail.transports.log import LogTransport
from avalon.mail.transports.smtp import SmtpTransport

__all__ = ["ArrayTransport", "LogTransport", "SmtpTransport"]
