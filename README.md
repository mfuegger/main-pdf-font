# pdf2font
Extracts info on the main font of a single or more pdfs.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Analyze all PDFs in current directory
python pdf2font.py

# Analyze all PDFs in a specific directory
python pdf2font.py /path/to/pdfs
python pdf2font.py ./documents

# Analyze a single PDF file
python pdf2font.py my_document.pdf

# Specify font size threshold for red highlighting (default: 10.0 pt)
python pdf2font.py --pt 9.0
python pdf2font.py /path/to/pdfs --pt 12.0

# Show help
python pdf2font.py -h
```

The script intelligently detects whether the argument is a file or directory and acts accordingly. When analyzing multiple PDFs, font sizes below the threshold (default 10pt) are highlighted in red.
