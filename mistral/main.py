import os
from pathlib import Path

from dotenv import load_dotenv
from mistralai import DocumentURLChunk, Mistral
from mistralai.models import OCRResponse
from tqdm import tqdm

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str


def get_combined_markdown(ocr_response: OCRResponse) -> str:
    markdowns: list[str] = []
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)


def main(reprocess=False):
    pdf_files = list(Path("../test_pdf").glob("*.pdf"))
    progress_bar = tqdm(pdf_files, unit="file")
    for pdf_file in progress_bar:
        markdown_path = Path(f"../mixtral_test_md/{pdf_file.stem}.md")

        # Skip if markdown already exists and reprocess flag is False
        if markdown_path.exists() and not reprocess:
            progress_bar.set_description(f"Skipping {pdf_file.stem} (already exists)")
            continue

        progress_bar.set_description(f"Processing {pdf_file.stem}")
        uploaded_file = client.files.upload(
            file={
                "file_name": pdf_file.stem,
                "content": pdf_file.read_bytes(),
            },
            purpose="ocr",
        )

        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

        pdf_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
            include_image_base64=True,
        )
        markdown = get_combined_markdown(pdf_response)
        os.makedirs("../mixtral_test_md", exist_ok=True)
        with open(f"../mixtral_test_md/{pdf_file.stem}.md", "w") as f:
            f.write(markdown)


if __name__ == "__main__":
    # Change to True if you want to reprocess existing files
    main(reprocess=False)
