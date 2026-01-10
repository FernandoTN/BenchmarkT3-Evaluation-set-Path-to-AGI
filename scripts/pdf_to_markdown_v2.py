#!/usr/bin/env python3
"""Convert PDF files to Markdown format using PyMuPDF for better extraction."""

import sys
from pathlib import Path
import fitz  # PyMuPDF


def pdf_to_markdown(pdf_path: Path) -> str:
    """Extract text from PDF using PyMuPDF and format as Markdown."""
    doc = fitz.open(pdf_path)

    lines = [f"# {pdf_path.stem}\n"]

    for i, page in enumerate(doc, 1):
        # Extract text with better layout preservation
        text = page.get_text("text")

        if text and text.strip():
            lines.append(f"\n## Page {i}\n")
            lines.append(text.strip())
        else:
            # Page might be image-only, note it
            lines.append(f"\n## Page {i}\n")
            lines.append("*[This page contains images/figures only - no extractable text]*")

    doc.close()
    return "\n".join(lines)


def convert_pdfs(pdf_files: list[Path], output_dir: Path = None):
    """Convert multiple PDFs to Markdown files."""
    for pdf_path in pdf_files:
        print(f"Converting: {pdf_path.name}")

        try:
            markdown_content = pdf_to_markdown(pdf_path)

            out_dir = output_dir or pdf_path.parent
            md_path = out_dir / f"{pdf_path.stem}.md"

            md_path.write_text(markdown_content, encoding="utf-8")
            print(f"  -> Created: {md_path.name}")

        except Exception as e:
            print(f"  -> Error: {e}", file=sys.stderr)


def main():
    if len(sys.argv) > 1:
        pdf_files = [Path(p) for p in sys.argv[1:]]
    else:
        pdf_files = list(Path(".").glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Found {len(pdf_files)} PDF file(s)\n")
    convert_pdfs(pdf_files)
    print("\nDone!")


if __name__ == "__main__":
    main()
