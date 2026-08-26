"""Run one Modian scrape and append the result to Notion."""

import os
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

from .modian_scraper import get_modian_star
from .notion_writer import NotionWriter

SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _required_environment() -> Dict[str, str]:
    """Return required configuration or fail before doing external work."""
    names = ("MODIAN_URL", "NOTION_TOKEN", "NOTION_DATABASE_ID")
    values = {name: os.environ.get(name, "").strip() for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return values


def run() -> dict:
    """Scrape the current count and create one new Notion page."""
    environment = _required_environment()

    star_count = get_modian_star(environment["MODIAN_URL"])
    if star_count < 0:
        raise ValueError("Modian star count must be a non-negative integer")

    collected_at = datetime.now(SHANGHAI_TIMEZONE)
    writer = NotionWriter(
        token=environment["NOTION_TOKEN"],
        database_id=environment["NOTION_DATABASE_ID"],
    )
    page = writer.create_modian_star_page(collected_at, star_count)

    page_id = page.get("id", "unknown")
    print(
        f"Created Notion page {page_id} for {collected_at:%Y-%m-%d} "
        f"with star count {star_count}"
    )
    return page


def main() -> None:
    run()


if __name__ == "__main__":
    main()
