import os
import pymupdf4llm
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from pdf_downloader import PDFDownloader
from openalex_downloader import OpenAlexDownloader
from lingua import LanguageDetectorBuilder

DATA_DIR = Path.cwd() / "data"
METADATA_DIR = DATA_DIR / "metadata"
PDFS_DIR = DATA_DIR / "pdfs"
EXTRACTED_DIR = DATA_DIR / "extracted"
SENTENCES_DIR = DATA_DIR / "sentences"


def generate_language_corpus(
    lang_code: str,
    max_articles: int,
    download_metadata: bool = False,
    download_pdfs: bool = False,
    generate_markdown: bool = False,
):
    """
    Generate language corpus from OpenAlex database articles

    Args:
        lang_code: Language code (e.g., 'he', 'lv')
        max_articles: Maximum number of articles to fetch
        download_metadata: If True, fetch fresh metadata from OpenAlex
        download_pdfs: If True, download PDFs from URLs in metadata
        generate_markdown: If True, convert PDFs to markdown
    """

    # Create language-specific directories
    lang_pdf_dir = PDFS_DIR / lang_code
    lang_extracted_dir = EXTRACTED_DIR / lang_code
    lang_sentences_dir = SENTENCES_DIR / lang_code

    for dir_path in [lang_pdf_dir, lang_extracted_dir, lang_sentences_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Setup tools
    lang_detector = LanguageDetectorBuilder.from_all_languages().build()
    metadata_path = METADATA_DIR / f"{lang_code}_article_data.csv"

    # Step 1: Download or load metadata
    if download_metadata:
        print(f"Fetching article metadata for {lang_code}...")
        openalex_downloader = OpenAlexDownloader(str(METADATA_DIR))
        articles_df = openalex_downloader.download_articles(lang_code, max_articles)
    else:
        print(f"Loading existing metadata for {lang_code}...")
        if not metadata_path.exists():
            print(f"No metadata found at {metadata_path}. Set download_metadata=True")
            return
        articles_df = pd.read_csv(metadata_path)

    if articles_df.empty:
        print(f"No articles found for {lang_code}")
        return

    # Step 2: Download PDFs
    if download_pdfs:
        print(f"Downloading PDFs for {lang_code}...")
        pdf_downloader = PDFDownloader(str(lang_pdf_dir))

        for idx, article in tqdm(
            articles_df.iterrows(),
            total=len(articles_df),
            desc=f"Downloading {lang_code} articles...",
        ):
            try:
                pdf_downloader.download_pdf(article["pdf_url"])
            except Exception as e:
                print(f"Error downloading article {idx}: {str(e)}")
                continue

    # Step 3: Convert PDFs to markdown
    if generate_markdown:
        print(f"Generating markdown for {lang_code}...")
        pdf_files = list(lang_pdf_dir.glob("*.pdf"))

        for idx, pdf_path in tqdm(
            enumerate(pdf_files),
            total=len(pdf_files),
            desc=f"Processing {lang_code} articles...",
        ):
            try:
                # Convert to markdown
                md_text = pymupdf4llm.to_markdown(str(pdf_path))

                # Detect language
                language = lang_detector.detect_language_of(md_text)
                print(f"Detected language: {language}")

                if language and language.iso_code_639_1.name.lower() == lang_code:
                    new_pdf_path = lang_pdf_dir / f"{idx}.pdf"
                    pdf_path.rename(new_pdf_path)

                    md_path = lang_extracted_dir / f"{idx}.md"
                    md_path.write_text(md_text, encoding="utf-8")
                else:
                    pdf_path.unlink()

            except Exception as e:
                print(f"Error processing {pdf_path.name}: {e}")
                pdf_path.unlink(missing_ok=True)
                continue


def main():
    """Create directories and generate corpora for target languages."""

    for dir_path in [DATA_DIR, METADATA_DIR, PDFS_DIR, EXTRACTED_DIR, SENTENCES_DIR]:
        os.makedirs(dir_path, exist_ok=True)

    # Generate corpora
    languages = [
        # ("he", 100),
        # ("lv", 100),
        ("ta", 100),
        # ("th", 100),
        # ("en", 100),
        # ("es", 100),
    ]

    for lang_code, max_articles in languages:
        generate_language_corpus(
            lang_code,
            max_articles,
            download_metadata=True,
            download_pdfs=True,
            generate_markdown=True,
        )


if __name__ == "__main__":
    main()
