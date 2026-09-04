"""DatabaseSeeder — entry point for `python grail db:seed` / `migrate --seed`."""

from __future__ import annotations

from database.seeders.demo_seeder import DemoSeeder

from avalon.orm import Seeder


class DatabaseSeeder(Seeder):
    """DatabaseSeeder."""

    async def run(self) -> None:
        await self.call([DemoSeeder])
