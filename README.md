# PaintPriceSheetGenerator

This project will generate a printable price sheet for paint products.

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Generate a PDF price sheet from a list of paint identifiers using the
command line interface:

```bash
python -m src.cli --input-file SKUs.json --output-file output/price_sheet.pdf
```

The CLI accepts a CSV or JSON file of identifiers and produces a themed
PDF.  Additional options allow customising the colours and fonts:

```
--header-text TEXT        Text to display in the document header
--header-color COLOR      Header background colour
--text-color COLOR        Default text colour
--background-color COLOR  Page background colour
--font-family NAME        Font family to use
```

Run tests with:

```bash
pytest
```

Data files can be stored in the `data/` directory.

