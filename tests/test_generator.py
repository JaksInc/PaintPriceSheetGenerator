import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import generator  # type: ignore


def test_generate_price_sheet(tmp_path: Path, monkeypatch) -> None:
    data = [
        {"product_id": "1", "name": "Red Paint", "price": "$10"},
        {"product_id": "2", "name": "Blue Paint", "price": "$12"},
    ]
    theme = generator.Theme(
        header_text="Test Sheet",
        header_color="#FF0000",
        text_color="#000000",
        background_color="#FFFFFF",
        font_family="Arial",
    )
    captured = {}

    class DummyHTML:
        def __init__(self, string: str):
            captured["html"] = string

        def write_pdf(self, filename: str) -> None:
            Path(filename).write_bytes(b"%PDF-1.4\n%%EOF")

    monkeypatch.setattr(generator, "HTML", DummyHTML)

    output = tmp_path / "sheet.pdf"
    generator.generate_price_sheet(data, theme, output)
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")
    html = captured["html"]
    assert "Test Sheet" in html
    assert "#FF0000" in html
