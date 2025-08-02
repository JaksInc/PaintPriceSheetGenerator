"""Load paint identifiers from a CSV or JSON file.

The module exposes :func:`load_ids` which reads a file containing paint
identifiers and returns them as a list. The loader accepts either CSV or
JSON input. JSON files may contain JavaScript style ``//`` comments which
are stripped before parsing.
"""

from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

_ID_RE = re.compile(r"^\d+$")


def _is_valid(value: str) -> bool:
    """Return ``True`` if *value* looks like a valid paint identifier.

    Invalid identifiers are logged and skipped by :func:`load_ids`.
    """

    if _ID_RE.fullmatch(value):
        return True
    logger.warning("Invalid paint id '%s' skipped", value)
    return False


def _strip_json_comments(text: str) -> str:
    """Remove ``//`` comments from *text* so it can be parsed as JSON."""

    return re.sub(r"//.*", "", text)


def _extract_from_obj(obj: object) -> List[str]:
    """Recursively extract identifier strings from *obj*."""

    ids: List[str] = []
    if isinstance(obj, dict):
        for value in obj.values():
            ids.extend(_extract_from_obj(value))
    elif isinstance(obj, list):
        for item in obj:
            ids.extend(_extract_from_obj(item))
    elif isinstance(obj, str) and _is_valid(obj):
        ids.append(obj)
    return ids


def _load_json(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(_strip_json_comments(text))
    return _extract_from_obj(data)


def _load_csv(path: Path) -> List[str]:
    ids: List[str] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        for row in reader:
            for cell in row:
                cell = cell.strip()
                if _is_valid(cell):
                    ids.append(cell)
    return ids


def load_ids(path: str | Path) -> List[str]:
    """Load paint identifiers from *path*.

    Parameters
    ----------
    path:
        Path to a JSON or CSV file containing paint identifiers.

    Returns
    -------
    list[str]
        List of validated paint identifiers.
    """

    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".json":
        return _load_json(p)
    if suffix == ".csv":
        return _load_csv(p)
    raise ValueError(f"Unsupported file format: {p.suffix}")
