"""Create the public storage symlink (Laravel ``storage:link``)."""

from __future__ import annotations

import os
from pathlib import Path

from avalon.console.command import Command


class StorageLinkCommand(Command):
    signature = "storage:link {--relative} {--force}"
    description = "Create the symbolic links configured for the application"

    def handle(self) -> int:
        links = dict(self.app.config.get("filesystems.links") or {})
        if not links:
            links = {"public/storage": "storage/app/public"}

        relative = bool(self.option("relative"))
        force = bool(self.option("force"))
        base = Path(self.app.base_path)

        for link, target in links.items():
            link_path = base / link
            target_path = base / target
            target_path.mkdir(parents=True, exist_ok=True)
            link_path.parent.mkdir(parents=True, exist_ok=True)

            if link_path.exists() or link_path.is_symlink():
                if force:
                    if link_path.is_symlink() or link_path.is_file():
                        link_path.unlink()
                    else:
                        self.error(f"The [{link}] link already exists and is not a symlink.")
                        return 1
                else:
                    self.warn(f"The [{link}] link already exists.")
                    continue

            if relative:
                target_arg = os.path.relpath(target_path, start=link_path.parent)
            else:
                target_arg = str(target_path)

            link_path.symlink_to(target_arg, target_is_directory=True)
            self.info(f"The [{link}] link has been connected to [{target}].")

        return 0
