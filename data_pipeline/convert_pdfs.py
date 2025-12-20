"""
PDF to Markdown Conversion

This script converts downloaded PDFs to markdown format using PyMuPDF.
It also performs language detection to filter out incorrectly classified articles,
keeping only those in the target language.
"""

import os
import pymupdf
import pymupdf4llm
import pandas as pd
from tqdm import tqdm
from utils import load_config
from lingua import LanguageDetectorBuilder


def detect_language(text: str, detector):
    """Detect the language of the given text."""
    result = detector.detect_language_of(text)
    return result.iso_code_639_1.name.lower() if result else None


def main():
    config = load_config()
    processing_stats = []
    detector = LanguageDetectorBuilder.from_all_languages().build()

    for lang_code, lang_config in config["LANGUAGES"].items():
        lang_pdf_dir = f"{config['directory']['PDFS_DIR']}/{lang_code}"
        lang_extracted_dir = f"{config['directory']['EXTRACTED_DIR']}/{lang_code}"
        os.makedirs(lang_extracted_dir, exist_ok=True)

        if not os.path.exists(lang_pdf_dir):
            continue

        pdf_files = list(
            set([path for path in os.listdir(lang_pdf_dir) if path.endswith(".pdf")])
        )
        kept_count = 0
        wrong_lang_count = 0
        error_count = 0

        for pdf_name in tqdm(
            pdf_files,
            total=len(pdf_files),
            desc=f"Processing {lang_config['name']}",
            bar_format=config["PROGRESS_BAR_FORMAT"],
        ):
            try:
                # Convert PDF to markdown
                pdf_path = os.path.join(lang_pdf_dir, pdf_name)
                with pymupdf.open(pdf_path) as doc:
                    md_text = pymupdf4llm.to_markdown(doc)

                # Verify language
                detected_code = detect_language(md_text, detector)
                if detected_code == lang_code:
                    # Rename PDF and save markdown
                    new_pdf_path = os.path.join(lang_pdf_dir, f"{kept_count}.pdf")
                    os.rename(pdf_path, new_pdf_path)

                    md_path = os.path.join(lang_extracted_dir, f"{kept_count}.md")
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(md_text)
                    kept_count += 1
                else:
                    # Remove PDF if wrong language
                    os.remove(pdf_path)
                    wrong_lang_count += 1

            except Exception as e:
                print(f"Error converting PDF to markdown: {str(e)}")
                os.remove(pdf_path)
                error_count += 1

        processing_stats.append(
            {
                "Language": lang_config["name"],
                "Total PDFs": len(pdf_files),
                "Kept": kept_count,
                "Wrong Language": wrong_lang_count,
                "Errors": error_count,
                "Success Rate": (
                    f"{kept_count / len(pdf_files) * 100:.1f}%" if pdf_files else "0%"
                ),
            }
        )

    print("PDF Processing Summary:")
    print(pd.DataFrame(processing_stats))
    print()
