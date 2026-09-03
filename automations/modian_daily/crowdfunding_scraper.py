"""Scrape the optimistic-count metric from a public Modian crowdfunding page."""

import logging
import time
from typing import Sequence

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

LOGGER = logging.getLogger(__name__)
CROWDFUNDING_STAR_COUNT_SELECTOR = ".appointment-people span[subscribe_count]"
DEFAULT_WAIT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_DELAYS_SECONDS = (5, 15)


class ModianCrowdfundingScrapeError(RuntimeError):
    """Raised when the crowdfunding count cannot be scraped after all attempts."""


def _chrome_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,2000")
    return options


def _parse_star_count(text: str) -> int:
    normalized = "".join(text.split()).replace(",", "")
    if not normalized or not normalized.isdecimal():
        raise ValueError(f"Unexpected Modian crowdfunding star count: {text!r}")

    star_count = int(normalized)
    if star_count < 0:
        raise ValueError("Modian crowdfunding star count must be non-negative")
    return star_count


def _loaded_star_count_text(driver: webdriver.Chrome):
    element = driver.find_element(By.CSS_SELECTOR, CROWDFUNDING_STAR_COUNT_SELECTOR)
    text = element.text.strip()
    return text if text else False


def _scrape_once(url: str, wait_timeout_seconds: int) -> int:
    driver = None
    try:
        driver = webdriver.Chrome(options=_chrome_options())
        driver.get(url)
        text = WebDriverWait(driver, wait_timeout_seconds).until(
            _loaded_star_count_text
        )
        return _parse_star_count(text)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                LOGGER.exception("Failed to quit the Chrome driver cleanly")


def get_modian_crowdfunding_star(
    url: str,
    wait_timeout_seconds: int = DEFAULT_WAIT_TIMEOUT_SECONDS,
    retry_delays_seconds: Sequence[int] = DEFAULT_RETRY_DELAYS_SECONDS,
) -> int:
    """Return the crowdfunding count, retrying each failure in a fresh browser."""
    if not url or not url.strip():
        raise ValueError("Modian crowdfunding URL must not be empty")
    if wait_timeout_seconds <= 0:
        raise ValueError("Wait timeout must be greater than zero")

    attempts = len(retry_delays_seconds) + 1
    for attempt in range(1, attempts + 1):
        try:
            return _scrape_once(url.strip(), wait_timeout_seconds)
        except Exception as error:
            if attempt == attempts:
                raise ModianCrowdfundingScrapeError(
                    "Failed to scrape Modian crowdfunding star count "
                    f"after {attempts} attempts"
                ) from error

            delay = retry_delays_seconds[attempt - 1]
            LOGGER.warning(
                "Modian crowdfunding scrape attempt %s/%s failed; "
                "retrying in %s seconds: %s",
                attempt,
                attempts,
                delay,
                error,
            )
            time.sleep(delay)

    raise AssertionError("unreachable")
