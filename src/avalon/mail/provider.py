"""Mail service provider."""

from __future__ import annotations

from avalon.mail.helpers import default_mail_config
from avalon.mail.mailer import Mail, MailManager
from avalon.providers.provider import ServiceProvider


class MailServiceProvider(ServiceProvider):
    """Binds mail manager from ``config/mail``."""

    def register(self) -> None:
        app = self.app

        def factory(_container):
            config = dict(app.config.get("mail") or {})
            if not config:
                config = default_mail_config()
            manager = MailManager(app, config)
            Mail.set_manager(manager)
            return manager

        app.container.singleton(MailManager, factory)
        app.container.alias(MailManager, "mail")

    def boot(self) -> None:
        if self.app.container.bound(MailManager):
            Mail.set_manager(self.app.make(MailManager))
