import unittest
from unittest.mock import Mock, patch

from automations.modian_daily import crowdfunding_main

ENVIRONMENT = {
    "MODIAN_CROWDFUNDING_URL": "https://zhongchou.modian.com/item/159828",
    "NOTION_TOKEN": "notion-token",
    "NOTION_CROWDFUNDING_DATABASE_ID": "crowdfunding-database-id",
}


class CrowdfundingMainTest(unittest.TestCase):
    def test_run_scrapes_and_creates_one_page_in_crowdfunding_database(self):
        writer = Mock()
        writer.create_crowdfunding_star_page.return_value = {
            "id": "crowdfunding-page-id"
        }

        with patch.dict(
            crowdfunding_main.os.environ, ENVIRONMENT, clear=True
        ), patch.object(
            crowdfunding_main, "get_modian_crowdfunding_star", return_value=1051
        ) as scrape, patch.object(
            crowdfunding_main,
            "CrowdfundingNotionWriter",
            return_value=writer,
        ) as writer_class:
            result = crowdfunding_main.run()

        self.assertEqual(result, {"id": "crowdfunding-page-id"})
        scrape.assert_called_once_with(ENVIRONMENT["MODIAN_CROWDFUNDING_URL"])
        writer_class.assert_called_once_with(
            token=ENVIRONMENT["NOTION_TOKEN"],
            database_id=ENVIRONMENT["NOTION_CROWDFUNDING_DATABASE_ID"],
        )
        collected_at, star_count = (
            writer.create_crowdfunding_star_page.call_args.args
        )
        self.assertEqual(star_count, 1051)
        self.assertEqual(getattr(collected_at.tzinfo, "key", None), "Asia/Shanghai")

    def test_uses_only_crowdfunding_database_environment_name(self):
        environment = dict(ENVIRONMENT)
        environment["NOTION_DATABASE_ID"] = "original-database-id"

        with patch.dict(
            crowdfunding_main.os.environ, environment, clear=True
        ):
            values = crowdfunding_main._required_environment()

        self.assertEqual(
            values["NOTION_CROWDFUNDING_DATABASE_ID"],
            "crowdfunding-database-id",
        )
        self.assertNotIn("NOTION_DATABASE_ID", values)

    def test_missing_crowdfunding_database_fails_before_scraping(self):
        environment = dict(ENVIRONMENT)
        del environment["NOTION_CROWDFUNDING_DATABASE_ID"]
        environment["NOTION_DATABASE_ID"] = "original-database-id"

        with patch.dict(
            crowdfunding_main.os.environ, environment, clear=True
        ), patch.object(
            crowdfunding_main, "get_modian_crowdfunding_star"
        ) as scrape:
            with self.assertRaisesRegex(
                RuntimeError, "NOTION_CROWDFUNDING_DATABASE_ID"
            ):
                crowdfunding_main.run()

        scrape.assert_not_called()

    def test_notion_failure_propagates(self):
        writer = Mock()
        writer.create_crowdfunding_star_page.side_effect = RuntimeError(
            "Notion failed"
        )

        with patch.dict(
            crowdfunding_main.os.environ, ENVIRONMENT, clear=True
        ), patch.object(
            crowdfunding_main, "get_modian_crowdfunding_star", return_value=1051
        ), patch.object(
            crowdfunding_main, "CrowdfundingNotionWriter", return_value=writer
        ):
            with self.assertRaisesRegex(RuntimeError, "Notion failed"):
                crowdfunding_main.run()


if __name__ == "__main__":
    unittest.main()
