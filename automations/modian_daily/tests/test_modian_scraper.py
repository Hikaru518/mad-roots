import unittest
from unittest.mock import Mock, call, patch

from automations.modian_daily import modian_scraper


class ModianScraperTest(unittest.TestCase):
    def test_scrape_once_returns_count_and_quits_driver(self):
        driver = Mock()

        with patch.object(
            modian_scraper.webdriver, "Chrome", return_value=driver
        ) as chrome, patch.object(modian_scraper, "WebDriverWait") as wait:
            wait.return_value.until.return_value = "1,032"

            result = modian_scraper._scrape_once(
                "https://m.modian.com/idea/2951.html", 30
            )

        self.assertEqual(result, 1032)
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
        driver.get.assert_called_once_with("https://m.modian.com/idea/2951.html")
        wait.assert_called_once_with(driver, 30)
        wait.return_value.until.assert_called_once_with(
            modian_scraper._loaded_star_count_text
        )
        driver.quit.assert_called_once_with()

    def test_scrape_once_quits_driver_when_page_parsing_fails(self):
        driver = Mock()
        element = Mock(text="not-a-number")

        with patch.object(
            modian_scraper.webdriver, "Chrome", return_value=driver
        ), patch.object(modian_scraper, "WebDriverWait") as wait:
            wait.return_value.until.return_value = element.text

            with self.assertRaises(ValueError):
                modian_scraper._scrape_once("https://example.com", 30)

        driver.quit.assert_called_once_with()

    def test_scrape_once_quits_driver_when_wait_times_out(self):
        driver = Mock()

        with patch.object(
            modian_scraper.webdriver, "Chrome", return_value=driver
        ), patch.object(modian_scraper, "WebDriverWait") as wait:
            wait.return_value.until.side_effect = TimeoutError("page timed out")

            with self.assertRaises(TimeoutError):
                modian_scraper._scrape_once("https://example.com", 30)

        driver.quit.assert_called_once_with()

    def test_parse_star_count_rejects_empty_and_non_numeric_values(self):
        for value in ("", "   ", "unknown", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                modian_scraper._parse_star_count(value)

    def test_parse_star_count_accepts_redirected_project_page_text(self):
        self.assertEqual(modian_scraper._parse_star_count("1,052人看好"), 1052)

    def test_loaded_star_count_ignores_placeholder(self):
        driver = Mock()
        placeholder = Mock(text="--人看好")
        driver.find_elements.return_value = [placeholder]

        self.assertFalse(modian_scraper._loaded_star_count_text(driver))

        placeholder.text = "1,052人看好"
        self.assertEqual(
            modian_scraper._loaded_star_count_text(driver), "1,052人看好"
        )
        driver.find_elements.assert_called_with(
            modian_scraper.By.CSS_SELECTOR,
            modian_scraper.STAR_COUNT_SELECTOR,
        )

    def test_get_modian_star_retries_with_expected_delays(self):
        with patch.object(
            modian_scraper,
            "_scrape_once",
            side_effect=[RuntimeError("first"), RuntimeError("second"), 1032],
        ) as scrape_once, patch.object(modian_scraper.time, "sleep") as sleep:
            result = modian_scraper.get_modian_star("https://example.com")

        self.assertEqual(result, 1032)
        self.assertEqual(scrape_once.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(5), call(15)])

    def test_get_modian_star_raises_after_all_attempts(self):
        with patch.object(
            modian_scraper,
            "_scrape_once",
            side_effect=RuntimeError("still failing"),
        ), patch.object(modian_scraper.time, "sleep"):
            with self.assertRaises(modian_scraper.ModianScrapeError):
                modian_scraper.get_modian_star("https://example.com")


if __name__ == "__main__":
    unittest.main()
