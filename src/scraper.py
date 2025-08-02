import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from src import input_loader

logger = logging.getLogger(__name__)

BASE_URL = "https://example.com/products/{}"
HEADERS = {"User-Agent": "PaintPriceSheetGenerator/1.0"}

# Default location used when caching is enabled
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"


def fetch_paint_price(
    product_id: str,
    session: Optional[requests.Session] = None,
    retries: int = 3,
    backoff_factor: float = 1.0,
    delay: float = 0.0,
    use_cache: bool = False,
    cache_dir: Path = CACHE_DIR,
) -> Optional[Dict[str, str]]:
    """Fetch price and basic details for a paint product.

    The function downloads the product page, handling HTTP errors and
    rate limiting. It then parses the page with :class:`BeautifulSoup`
    to extract the product name and price, returning them in a
    dictionary. If any step fails ``None`` is returned.

    Parameters
    ----------
    product_id:
        Identifier for the product in the remote catalogue.
    session:
        Optional :class:`requests.Session` to use for the HTTP
        request. A new session is created if not supplied.
    retries:
        Number of times to retry the request when it fails or the
        server responds with a rate-limit status code.
    backoff_factor:
        Initial delay between retries. The delay is doubled after each
        failed attempt.
    delay:
        Seconds to wait before each request. This helps to avoid hitting
        remote rate limits when scraping many products.
    use_cache:
        If ``True``, responses are cached on disk and reused for
        subsequent requests.  The cache is stored under ``cache_dir`` and
        contains JSON files keyed by product identifier.
    cache_dir:
        Directory where cache files are stored when ``use_cache`` is
        enabled.
    """

    sess = session or requests.Session()
    url = BASE_URL.format(product_id)

    if use_cache:
        cache_file = Path(cache_dir) / f"{product_id}.json"
        if cache_file.exists():
            try:
                return json.loads(cache_file.read_text())
            except json.JSONDecodeError:
                logger.warning("Cache file %s is corrupted; refetching", cache_file)

    for attempt in range(1, retries + 1):
        try:
            if delay > 0:
                time.sleep(delay)
            response = sess.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 429:
                logger.warning(
                    "Rate limited when requesting %s (attempt %s/%s)",
                    product_id,
                    attempt,
                    retries,
                )
                time.sleep(backoff_factor)
                backoff_factor *= 2
                continue
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error(
                "Failed to fetch %s: %s", product_id, exc, exc_info=True
            )
            if attempt == retries:
                return None
            time.sleep(backoff_factor)
            backoff_factor *= 2
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.select_one(".price")
        name_tag = soup.select_one("h1")

        if not price_tag or not name_tag:
            logger.error("Could not parse product details for %s", product_id)
            return None

        price = price_tag.get_text(strip=True)
        name = name_tag.get_text(strip=True)

        info = {"product_id": product_id, "name": name, "price": price}

        if use_cache:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            cache_file = Path(cache_dir) / f"{product_id}.json"
            cache_file.write_text(json.dumps(info))

        logger.info("Fetched product %s (%s) at price %s", product_id, name, price)
        return info

    return None


def main() -> None:
    """Command-line interface for fetching paint prices."""

    parser = argparse.ArgumentParser(description="Fetch paint product prices")
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path(__file__).with_name("SKUs.json"),
        help="CSV or JSON file containing paint IDs.",
    )
    args = parser.parse_args()

    ids = input_loader.load_ids(args.input_file)

    sess = requests.Session()
    for pid in ids:
        fetch_paint_price(pid, session=sess)


if __name__ == "__main__":
    main()
