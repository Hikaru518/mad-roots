import unittest
from unittest.mock import Mock, call, patch

from automations.modian_daily import crowdfunding_scraper


class CrowdfundingScraperTest(unittest.TestCase):
    def test_scrape_once_waits_for_loaded_count_and_quits_driver(self):
        driver = Mock()

        with patch.object(
            crowdfunding_scraper.webdriver, "Chrome", return_value=driver
        ) as chrome, patch.object(crowdfunding_scraper, "WebDriverWait") as wait:
            wait.return_value.until.return_value = "1,051"

            result = crowdfunding_scraper._scrape_once(
                "https://zhongchou.modian.com/item/159828", 30
            )

        self.assertEqual(result, 1051)
        chrome.assert_called_once()
        chrome_arguments = set(chrome.call_args.kwargs["options"].arguments)
        self.assertTrue(
            {
                "--headless=new",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--window-size=1280,2000",
            }.issubset(chrome_arguments)
        )
        driver.get.assert_called_once_with(
            "https://zhongchou.modian.com/item/159828"
        )
        wait.assert_called_once_with(driver, 30)
        wait.return_value.until.assert_called_once_with(
            crowdfunding_scraper._loaded_star_count_text
        )
        driver.quit.assert_called_once_with()

    def test_loaded_star_count_waits_for_nonempty_text(self):
        driver = Mock()
        element = Mock()
        driver.find_element.return_value = element

        element.text = ""
        self.assertFalse(crowdfunding_scraper._loaded_star_count_text(driver))

        element.text = " 1051 "
        self.assertEqual(
            crowdfunding_scraper._loaded_star_count_text(driver), "1051"
        )
        driver.find_element.assert_called_with(
            crowdfunding_scraper.By.CSS_SELECTOR,
            crowdfunding_scraper.CROWDFUNDING_STAR_COUNT_SELECTOR,
        )

    def test_scrape_once_quits_driver_when_wait_fails(self):
        driver = Mock()

        with patch.object(
            crowdfunding_scraper.webdriver, "Chrome", return_value=driver
        ), patch.object(crowdfunding_scraper, "WebDriverWait") as wait:
            wait.return_value.until.side_effect = TimeoutError("page timed out")

            with self.assertRaises(TimeoutError):
                crowdfunding_scraper._scrape_once("https://example.com", 30)

        driver.quit.assert_called_once_with()

    def test_parse_star_count_rejects_empty_and_non_numeric_values(self):
        for value in ("", "   ", "unknown", "1051人", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                crowdfunding_scraper._parse_star_count(value)

    def test_get_star_retries_with_expected_delays(self):
        with patch.object(
            crowdfunding_scraper,
            "_scrape_once",
            side_effect=[RuntimeError("first"), RuntimeError("second"), 1051],
        ) as scrape_once, patch.object(
            crowdfunding_scraper.time, "sleep"
        ) as sleep:
            result = crowdfunding_scraper.get_modian_crowdfunding_star(
                "https://example.com"
            )

        self.assertEqual(result, 1051)
        self.assertEqual(scrape_once.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(5), call(15)])

    def test_get_star_raises_after_all_attempts(self):
        with patch.object(
            crowdfunding_scraper,
            "_scrape_once",
            side_effect=RuntimeError("still failing"),
        ), patch.object(crowdfunding_scraper.time, "sleep"):
            with self.assertRaises(
                crowdfunding_scraper.ModianCrowdfundingScrapeError
            ):
                crowdfunding_scraper.get_modian_crowdfunding_star(
                    "https://example.com"
                )


if __name__ == "__main__":
    unittest.main()
