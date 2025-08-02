import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_loader import load_ids


def test_load_ids_from_json(tmp_path: Path) -> None:
    content = textwrap.dedent(
        """
        {
          // comment for group
          "group": {
            "a": "123",
            "b": ["456", "abc"]
          }
        }
        """
    )
    path = tmp_path / "ids.json"
    path.write_text(content)
    assert load_ids(path) == ["123", "456"]


def test_load_ids_from_csv(tmp_path: Path) -> None:
    csv_content = "123,abc\n456\n"
    path = tmp_path / "ids.csv"
    path.write_text(csv_content)
    assert load_ids(path) == ["123", "456"]
