"""Command line interface for PaintPriceSheetGenerator.

This module provides a small command line utility that wires together the
input loader, web scraper and PDF generator to produce a printable price
sheet.  It accepts options for the input file, output file and various
theming choices that control the look of the resulting PDF.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable, Dict, Any, List

from src import input_loader, scraper, generator

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """Create the :mod:`argparse` parser for the CLI."""

    parser = argparse.ArgumentParser(
        description="Generate a printable price sheet for paint products"
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path(__file__).with_name("SKUs.json"),
        help="CSV or JSON file containing paint IDs (default: %(default)s)",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path("output/price_sheet.pdf"),
        help="Destination for generated PDF (default: %(default)s)",
    )
    parser.add_argument(
        "--header-text",
        default=generator.Theme.header_text,
        help="Text to display in the document header",
    )
    parser.add_argument(
        "--header-color",
        default=generator.Theme.header_color,
        help="Colour of the header background",
    )
    parser.add_argument(
        "--text-color",
        default=generator.Theme.text_color,
        help="Default text colour",
    )
    parser.add_argument(
        "--background-color",
        default=generator.Theme.background_color,
        help="Page background colour",
    )
    parser.add_argument(
        "--font-family",
        default=generator.Theme.font_family,
        help="Font family to use",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=0.0,
        help="Seconds to wait between HTTP requests",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Directory to cache price data. Caching disabled by default",
    )
    return parser


def _scrape_prices(
    ids: Iterable[str], *, delay: float = 0.0, cache_dir: Path | None = None
) -> List[Dict[str, Any]]:
    """Fetch product information for all *ids*.

    Parameters
    ----------
    ids:
        Iterable of product identifiers.

    Returns
    -------
    list[dict]
        List of price information dictionaries as returned by
        :func:`scraper.fetch_paint_price`.  Entries that fail to
        download are skipped.
    """

    items: List[Dict[str, Any]] = []
    session = scraper.requests.Session()  # type: ignore[attr-defined]
    use_cache = cache_dir is not None
    for pid in ids:
        info = scraper.fetch_paint_price(
            pid,
            session=session,
            delay=delay,
            use_cache=use_cache,
            cache_dir=cache_dir or scraper.CACHE_DIR,
        )
        if info:
            items.append(info)
    return items


def main(argv: Iterable[str] | None = None) -> Path:
    """Run the command line interface.

    Parameters
    ----------
    argv:
        Optional iterable of strings representing command line arguments.

    Returns
    -------
    :class:`pathlib.Path`
        The path to the generated PDF file.
    """

    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    logging.basicConfig(level=logging.INFO)
    logger.info("Loading product identifiers from %s", args.input_file)
    ids = input_loader.load_ids(args.input_file)

    logger.info("Scraping prices for %d products", len(ids))
    items = _scrape_prices(
        ids, delay=args.request_delay, cache_dir=args.cache_dir
    )

    theme = generator.Theme(
        header_text=args.header_text,
        header_color=args.header_color,
        text_color=args.text_color,
        background_color=args.background_color,
        font_family=args.font_family,
    )

    logger.info("Generating price sheet: %s", args.output_file)
    return generator.generate_price_sheet(items, theme=theme, output_file=args.output_file)


if __name__ == "__main__":
    main()
