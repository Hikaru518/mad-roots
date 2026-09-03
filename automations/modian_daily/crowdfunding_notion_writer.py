"""Append crowdfunding star-count snapshots to a dedicated Notion database."""

from datetime import datetime
from typing import Any, Optional

from notion_client import Client

NOTION_API_VERSION = "2022-06-28"


class CrowdfundingNotionWriter:
    def __init__(
        self,
        token: str,
        database_id: str,
        client: Optional[Any] = None,
    ) -> None:
        if not token or not token.strip():
            raise ValueError("Notion token must not be empty")
        if not database_id or not database_id.strip():
            raise ValueError("Crowdfunding Notion database ID must not be empty")

        self._database_id = database_id.strip()
        self._client = client or Client(
            auth=token.strip(), notion_version=NOTION_API_VERSION
        )

    def create_crowdfunding_star_page(
        self, collected_at: datetime, star_count: int
    ) -> dict:
        if not isinstance(star_count, int) or isinstance(star_count, bool):
            raise TypeError("Modian crowdfunding star count must be an integer")
        if star_count < 0:
            raise ValueError("Modian crowdfunding star count must be non-negative")

        date_text = collected_at.strftime("%Y-%m-%d")
        properties = {
            "名称": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"{date_text} 众筹看好人数",
                        },
                    }
                ],
            },
            "日期": {
                "type": "date",
                "date": {"start": date_text},
            },
            "看好人数": {
                "type": "number",
                "number": star_count,
            },
        }
        return self._client.pages.create(
            parent={"database_id": self._database_id},
            properties=properties,
        )
