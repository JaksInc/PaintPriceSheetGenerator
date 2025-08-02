import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from generator import Theme, generate_price_sheet  # type: ignore


def test_generate_price_sheet(tmp_path: Path) -> None:
    data = [
        {"product_id": "1", "name": "Red Paint", "price": "$10"},
        {"product_id": "2", "name": "Blue Paint", "price": "$12"},
    ]
    theme = Theme(
        header_text="Test Sheet",
        header_color="#FF0000",
        text_color="#000000",
        background_color="#FFFFFF",
        font_family="Arial",
    )
    output = tmp_path / "sheet.pdf"
    generate_price_sheet(data, theme, output)
    assert output.exists()
    assert output.stat().st_size > 0
    assert output.read_bytes().startswith(b"%PDF")
