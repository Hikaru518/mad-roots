import os
from notion_client import Client
from datetime import datetime

notion = Client(auth=os.environ["NOTION_TOKEN"])
database_id = os.environ["NOTION_DATABASE_ID"]


def get_today() -> str:
    return datetime.today()


class ModianStarPage(object):
    def __init__(self, database_id: str) -> None:
        self.database_id = database_id
        self.creator = "bot"

    def create_new_modian_star_page(self, date: datetime, star_count: int) -> None:
        new_page = {
            "Date": {"type": "date", "date": {"start": date.strftime("%Y-%m-%d")}},
            "Star": {"type": "number", "number": star_count},
            "Creator": {
                "type": "rich_text",
                "rich_text": [{"type": "text", "text": {"content": self.creator}}],
            },
        }
        notion.pages.create(
            parent={"database_id": self.database_id}, properties=new_page
        )

    def query_page(self, page_id: str) -> dict:
        return notion.pages.retrieve(page_id=page_id)
