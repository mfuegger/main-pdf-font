"""Extract main font info from a single or more pdfs."""

import argparse
import logging
import os
import re
from collections import Counter
from pathlib import Path

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextContainer

logging.getLogger("pdfminer").setLevel(logging.ERROR)

def analyze_pdf(pdf_path: str | Path) -> tuple[str | None, float | None]:
    """Extract the most common font and size from a PDF file."""
    sizes: list[float] = []
    fonts: list[str] = []

    try:
        for page_layout in extract_pages(pdf_path):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    for text_line in element:
                        # text_line might be an LTChar directly
                        if isinstance(text_line, LTChar):
                            sizes.append(round(text_line.size, 1))
                            fonts.append(text_line.fontname)
                        else:
                            # Otherwise, try to iterate over characters in the line
                            try:
                                for character in text_line:
                                    if isinstance(character, LTChar):
                                        sizes.append(round(character.size, 1))
                                        fonts.append(character.fontname)
                            except TypeError:
                                # Skip non-iterable objects like LTAnno
                                pass
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None, None

    if not sizes:
        return None, None

    # find most common size and font
    size_counts = Counter(sizes)
    font_counts = Counter(fonts)
    main_size = size_counts.most_common(1)[0][0]
    main_font = font_counts.most_common(1)[0][0]

    return main_font, main_size


def summarize_all_pdfs_in_dir(directory: str | Path = ".", threshold: float = 10.0) -> None:
    """Summarize the main font/size for all PDFs in the specified directory."""
    dir_path = Path(directory)
    pdfs = [f.name for f in dir_path.iterdir() if f.suffix.lower() == ".pdf"]

    # Sort numerically by the leading number in the filename
    def extract_number(fname: str) -> int | float:
        m = re.match(r"(\d+)", fname)
        return int(m.group(1)) if m else float("inf")

    pdfs.sort(key=extract_number)

    print(f"Found {len(pdfs)} PDF files in {dir_path.resolve()}.\n")

    # ANSI color codes
    RED = "\033[31m"
    RESET = "\033[0m"

    for pdf in pdfs:
        pdf_path = dir_path / pdf
        main_font, main_size = analyze_pdf(pdf_path)
        if main_font is not None and main_size is not None:
            color = RED if main_size < threshold else RESET
            print(f"{pdf:<40} {color}{main_size:>4.1f} pt ({main_font}){RESET}")


def main() -> None:
    """Main entry point for the PDF font analyzer."""
    parser = argparse.ArgumentParser(
        description="Extract main font info from PDF files"
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a PDF file or directory (default: current directory)"
    )

    parser.add_argument(
        "--pt",
        type=float,
        default=10.0,
        help="Font size threshold for red highlighting (default: 10.0)"
    )

    args = parser.parse_args()

    path = Path(args.path)

    # If path is a file, analyze that file
    if path.is_file():
        font, size = analyze_pdf(path)
        if font and size:
            print(f"{path.name:<40} {size:.1f} pt ({font})")
        else:
            print(f"Could not analyze {path}")
    # If path is a directory, analyze all PDFs in it
    elif path.is_dir():
        summarize_all_pdfs_in_dir(path, args.pt)
    else:
        print(f"Error: '{path}' is not a valid file or directory")
        parser.print_help()


if __name__ == "__main__":
    main()
