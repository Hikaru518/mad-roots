import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

from automations.modian_daily.crowdfunding_notion_writer import (
    CrowdfundingNotionWriter,
)


class CrowdfundingNotionWriterTest(unittest.TestCase):
    def test_initializes_client_with_database_compatible_api_version(self):
        with patch(
            "automations.modian_daily.crowdfunding_notion_writer.Client"
        ) as client:
            CrowdfundingNotionWriter(" token ", " crowdfunding-database-id ")

        client.assert_called_once_with(auth="token", notion_version="2022-06-28")

    def test_create_page_uses_crowdfunding_database_and_schema(self):
        client = Mock()
        client.pages.create.return_value = {"id": "crowdfunding-page-id"}
        writer = CrowdfundingNotionWriter(
            "token", "crowdfunding-database-id", client=client
        )
        collected_at = datetime(2026, 9, 3, 3, 17, tzinfo=ZoneInfo("Asia/Shanghai"))

        result = writer.create_crowdfunding_star_page(collected_at, 1051)

        self.assertEqual(result, {"id": "crowdfunding-page-id"})
        client.pages.create.assert_called_once_with(
            parent={"database_id": "crowdfunding-database-id"},
            properties={
                "名称": {
                    "type": "title",
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": "2026-09-03 众筹看好人数",
                            },
                        }
                    ],
                },
                "日期": {
                    "type": "date",
                    "date": {"start": "2026-09-03"},
                },
                "看好人数": {
                    "type": "number",
                    "number": 1051,
                },
            },
        )

    def test_create_page_rejects_invalid_counts_without_api_call(self):
        client = Mock()
        writer = CrowdfundingNotionWriter(
            "token", "crowdfunding-database-id", client=client
        )

        invalid_counts = ((-1, ValueError), (True, TypeError), ("1", TypeError))
        for value, exception in invalid_counts:
            with self.subTest(value=value), self.assertRaises(exception):
                writer.create_crowdfunding_star_page(datetime.now(), value)

        client.pages.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
