def main():
    from pathlib import Path

    from docling.document_converter import DocumentConverter

    for file in Path("../test_pdf").glob("*.pdf"):
        print(f"Converting {file}")
        converter = DocumentConverter()
        result = converter.convert(file)
        file_md = Path("../test_md") / Path(file.stem + ".md")
        with open(f"{file.stem}.md", "w") as f:
            f.write(result.document.export_to_markdown())


if __name__ == "__main__":
    main()
