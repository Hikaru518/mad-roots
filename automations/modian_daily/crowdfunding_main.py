"""Run one Modian crowdfunding scrape and append the result to Notion."""

import os
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

from .crowdfunding_notion_writer import CrowdfundingNotionWriter
from .crowdfunding_scraper import get_modian_crowdfunding_star

SHANGHAI_TIMEZONE = ZoneInfo("Asia/Shanghai")


def _required_environment() -> Dict[str, str]:
    """Return crowdfunding configuration or fail before doing external work."""
    names = (
        "MODIAN_CROWDFUNDING_URL",
        "NOTION_TOKEN",
        "NOTION_CROWDFUNDING_DATABASE_ID",
    )
    values = {name: os.environ.get(name, "").strip() for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return values


def run() -> dict:
    """Scrape the current crowdfunding count and create one new Notion page."""
    environment = _required_environment()

    star_count = get_modian_crowdfunding_star(
        environment["MODIAN_CROWDFUNDING_URL"]
    )
    if star_count < 0:
        raise ValueError("Modian crowdfunding star count must be non-negative")

    collected_at = datetime.now(SHANGHAI_TIMEZONE)
    writer = CrowdfundingNotionWriter(
        token=environment["NOTION_TOKEN"],
        database_id=environment["NOTION_CROWDFUNDING_DATABASE_ID"],
    )
    page = writer.create_crowdfunding_star_page(collected_at, star_count)

    page_id = page.get("id", "unknown")
    print(
        f"Created crowdfunding Notion page {page_id} for "
        f"{collected_at:%Y-%m-%d} with star count {star_count}"
    )
    return page


def main() -> None:
    run()


if __name__ == "__main__":
    main()
