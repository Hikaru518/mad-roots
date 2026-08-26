import unittest
from unittest.mock import Mock, patch

from automations.modian_daily import main

ENVIRONMENT = {
    "MODIAN_URL": "https://m.modian.com/idea/2951.html",
    "NOTION_TOKEN": "notion-token",
    "NOTION_DATABASE_ID": "database-id",
}


class MainTest(unittest.TestCase):
    def test_run_scrapes_and_creates_one_page(self):
        writer = Mock()
        writer.create_modian_star_page.return_value = {"id": "page-id"}

        with patch.dict(main.os.environ, ENVIRONMENT, clear=True), patch.object(
            main, "get_modian_star", return_value=1032
        ) as scrape, patch.object(
            main, "NotionWriter", return_value=writer
        ) as writer_class:
            result = main.run()

        self.assertEqual(result, {"id": "page-id"})
        scrape.assert_called_once_with(ENVIRONMENT["MODIAN_URL"])
        writer_class.assert_called_once_with(
            token=ENVIRONMENT["NOTION_TOKEN"],
            database_id=ENVIRONMENT["NOTION_DATABASE_ID"],
        )
        collected_at, star_count = writer.create_modian_star_page.call_args.args
        self.assertEqual(star_count, 1032)
        self.assertEqual(getattr(collected_at.tzinfo, "key", None), "Asia/Shanghai")

    def test_missing_environment_fails_before_scraping(self):
        with patch.dict(main.os.environ, {}, clear=True), patch.object(
            main, "get_modian_star"
        ) as scrape:
            with self.assertRaisesRegex(RuntimeError, "MODIAN_URL"):
                main.run()

        scrape.assert_not_called()

    def test_notion_failure_propagates(self):
        writer = Mock()
        writer.create_modian_star_page.side_effect = RuntimeError("Notion failed")

        with patch.dict(main.os.environ, ENVIRONMENT, clear=True), patch.object(
            main, "get_modian_star", return_value=1032
        ), patch.object(main, "NotionWriter", return_value=writer):
            with self.assertRaisesRegex(RuntimeError, "Notion failed"):
                main.run()

    def test_two_successful_runs_create_two_pages(self):
        writer = Mock()
        writer.create_modian_star_page.side_effect = [
            {"id": "page-one"},
            {"id": "page-two"},
        ]

        with patch.dict(main.os.environ, ENVIRONMENT, clear=True), patch.object(
            main, "get_modian_star", return_value=1032
        ), patch.object(main, "NotionWriter", return_value=writer):
            first = main.run()
            second = main.run()

        self.assertEqual(first, {"id": "page-one"})
        self.assertEqual(second, {"id": "page-two"})
        self.assertEqual(writer.create_modian_star_page.call_count, 2)
        self.assertEqual(
            [item.args[1] for item in writer.create_modian_star_page.call_args_list],
            [1032, 1032],
        )


if __name__ == "__main__":
    unittest.main()
