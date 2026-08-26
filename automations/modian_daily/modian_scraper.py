"""Scrape the public Modian idea page with a headless Chrome browser."""

import logging
import time
from typing import Sequence

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LOGGER = logging.getLogger(__name__)
STAR_COUNT_SELECTOR = ".bottom_btn .total"
DEFAULT_WAIT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_DELAYS_SECONDS = (5, 15)


class ModianScrapeError(RuntimeError):
    """Raised when the Modian count cannot be scraped after all attempts."""


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
        raise ValueError(f"Unexpected Modian star count: {text!r}")

    star_count = int(normalized)
    if star_count < 0:
        raise ValueError("Modian star count must be non-negative")
    return star_count


def _scrape_once(url: str, wait_timeout_seconds: int) -> int:
    driver = None
    try:
        driver = webdriver.Chrome(options=_chrome_options())
        driver.get(url)
        element = WebDriverWait(driver, wait_timeout_seconds).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, STAR_COUNT_SELECTOR))
        )
        return _parse_star_count(element.text)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                LOGGER.exception("Failed to quit the Chrome driver cleanly")


def get_modian_star(
    url: str,
    wait_timeout_seconds: int = DEFAULT_WAIT_TIMEOUT_SECONDS,
    retry_delays_seconds: Sequence[int] = DEFAULT_RETRY_DELAYS_SECONDS,
) -> int:
    """Return the current count, retrying each failure in a fresh browser."""
    if not url or not url.strip():
        raise ValueError("Modian URL must not be empty")
    if wait_timeout_seconds <= 0:
        raise ValueError("Wait timeout must be greater than zero")

    attempts = len(retry_delays_seconds) + 1
    for attempt in range(1, attempts + 1):
        try:
            return _scrape_once(url.strip(), wait_timeout_seconds)
        except Exception as error:
            if attempt == attempts:
                raise ModianScrapeError(
                    f"Failed to scrape Modian star count after {attempts} attempts"
                ) from error

            delay = retry_delays_seconds[attempt - 1]
            LOGGER.warning(
                "Modian scrape attempt %s/%s failed; retrying in %s seconds: %s",
                attempt,
                attempts,
                delay,
                error,
            )
            time.sleep(delay)

    raise AssertionError("unreachable")
