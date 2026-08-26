"""Append Modian star-count snapshots to a Notion database."""

from datetime import datetime
from typing import Any, Optional

from notion_client import Client

NOTION_API_VERSION = "2022-06-28"


class NotionWriter:
    def __init__(
        self,
        token: str,
        database_id: str,
        client: Optional[Any] = None,
    ) -> None:
        if not token or not token.strip():
            raise ValueError("Notion token must not be empty")
        if not database_id or not database_id.strip():
            raise ValueError("Notion database ID must not be empty")

        self._database_id = database_id.strip()
        self._client = client or Client(
            auth=token.strip(), notion_version=NOTION_API_VERSION
        )

    def create_modian_star_page(self, collected_at: datetime, star_count: int) -> dict:
        if not isinstance(star_count, int) or isinstance(star_count, bool):
            raise TypeError("Modian star count must be an integer")
        if star_count < 0:
            raise ValueError("Modian star count must be non-negative")

        properties = {
            "Date": {
                "type": "date",
                "date": {"start": collected_at.strftime("%Y-%m-%d")},
            },
            "Star": {"type": "number", "number": star_count},
            "Creator": {
                "type": "rich_text",
                "rich_text": [{"type": "text", "text": {"content": "bot"}}],
            },
        }
        return self._client.pages.create(
            parent={"database_id": self._database_id},
            properties=properties,
        )
