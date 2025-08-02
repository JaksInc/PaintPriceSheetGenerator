"""Generate a PDF price sheet for paint products."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Dict, Any, List

from weasyprint import HTML


@dataclass
class Theme:
    """Formatting options for the generated price sheet.

    Attributes
    ----------
    header_text:
        Text to display at the top of the document.
    header_color:
        Color for the header background and table header cells.
    text_color:
        Default text color.
    background_color:
        Page background color.
    font_family:
        Font family to use throughout the document.
    """

    header_text: str = "Paint Price Sheet"
    header_color: str = "#333333"
    text_color: str = "#000000"
    background_color: str = "#FFFFFF"
    font_family: str = "Arial"


def generate_price_sheet(
    items: Iterable[Dict[str, Any]],
    theme: Theme | None = None,
    output_file: str | Path = "output/price_sheet.pdf",
) -> Path:
    """Generate a PDF price sheet from *items* using *theme* options.

    Parameters
    ----------
    items:
        Iterable of dictionaries with keys ``product_id``, ``name`` and ``price``.
    theme:
        :class:`Theme` instance specifying colours and fonts to use. If not
        supplied the default :class:`Theme` is used.
    output_file:
        Location of the generated PDF. The parent directory is created
        automatically if necessary.
    """

    theme = theme or Theme()

    rows: List[str] = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{item.get('product_id', '')}</td>"
            f"<td>{item.get('name', '')}</td>"
            f"<td>{item.get('price', '')}</td>"
            "</tr>"
        )

    table_rows = "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
body {{
    font-family: {theme.font_family}, sans-serif;
    color: {theme.text_color};
    background-color: {theme.background_color};
}}

h1 {{
    background-color: {theme.header_color};
    color: {theme.background_color};
    text-align: center;
    padding: 10px 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    border: 1px solid {theme.text_color};
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: {theme.header_color};
    color: {theme.background_color};
}}
</style>
</head>
<body>
<h1>{theme.header_text}</h1>
<table>
<thead><tr><th>ID</th><th>Name</th><th>Price</th></tr></thead>
<tbody>
{table_rows}
</tbody>
</table>
</body>
</html>
"""

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(str(output_path))
    return output_path
