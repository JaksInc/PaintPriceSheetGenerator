import pathlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import cli


class DummySession:
    pass


def test_cli_runs_pipeline(tmp_path, monkeypatch):
    # prepare input file
    input_file = tmp_path / "ids.csv"
    input_file.write_text("111\n222\n")

    items = [
        {"product_id": "111", "name": "Red", "price": "$1"},
        {"product_id": "222", "name": "Blue", "price": "$2"},
    ]

    def fake_fetch(pid, session=None):
        return next((i for i in items if i["product_id"] == pid), None)

    monkeypatch.setattr(cli.scraper, "fetch_paint_price", fake_fetch)
    monkeypatch.setattr(cli.scraper.requests, "Session", lambda: DummySession())

    captured = {}

    def fake_generate(data, theme, output_file):
        captured["items"] = list(data)
        captured["theme"] = theme
        captured["output_file"] = pathlib.Path(output_file)
        return captured["output_file"]

    monkeypatch.setattr(cli.generator, "generate_price_sheet", fake_generate)

    output = tmp_path / "out.pdf"
    cli.main(
        [
            "--input-file",
            str(input_file),
            "--output-file",
            str(output),
            "--header-text",
            "My Sheet",
            "--header-color",
            "#FF0000",
            "--text-color",
            "#00FF00",
            "--background-color",
            "#0000FF",
            "--font-family",
            "Comic Sans",
        ]
    )

    assert captured["items"] == items
    assert captured["output_file"] == output
    theme = captured["theme"]
    assert theme.header_text == "My Sheet"
    assert theme.header_color == "#FF0000"
    assert theme.text_color == "#00FF00"
    assert theme.background_color == "#0000FF"
    assert theme.font_family == "Comic Sans"
