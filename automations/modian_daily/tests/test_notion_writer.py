import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

from automations.modian_daily.notion_writer import NotionWriter


class NotionWriterTest(unittest.TestCase):
    def test_initializes_client_with_database_compatible_api_version(self):
        with patch("automations.modian_daily.notion_writer.Client") as client:
            NotionWriter(" token ", " database-id ")

        client.assert_called_once_with(auth="token", notion_version="2022-06-28")

    def test_create_page_uses_existing_schema(self):
        client = Mock()
        client.pages.create.return_value = {"id": "page-id"}
        writer = NotionWriter("token", "database-id", client=client)
        collected_at = datetime(2026, 8, 26, 3, 17, tzinfo=ZoneInfo("Asia/Shanghai"))

        result = writer.create_modian_star_page(collected_at, 1032)

        self.assertEqual(result, {"id": "page-id"})
        client.pages.create.assert_called_once_with(
            parent={"database_id": "database-id"},
            properties={
                "Date": {
                    "type": "date",
                    "date": {"start": "2026-08-26"},
                },
                "Star": {"type": "number", "number": 1032},
                "Creator": {
                    "type": "rich_text",
                    "rich_text": [{"type": "text", "text": {"content": "bot"}}],
                },
            },
        )

    def test_create_page_rejects_invalid_counts_without_api_call(self):
        client = Mock()
        writer = NotionWriter("token", "database-id", client=client)

        invalid_counts = ((-1, ValueError), (True, TypeError), ("1", TypeError))
        for value, exception in invalid_counts:
            with self.subTest(value=value), self.assertRaises(exception):
                writer.create_modian_star_page(datetime.now(), value)

        client.pages.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
