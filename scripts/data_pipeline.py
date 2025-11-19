import os
from pdf_processor import PDFProcessor
from openalex_downloader import OpenAlexDownloader

DATA_DIR = os.path.normpath("data/")
METADATA_DIR = os.path.join(DATA_DIR, "metadata")
PDFS_DIR = os.path.join(DATA_DIR, "pdfs")
EXTRACTED_DIR = os.path.join(DATA_DIR, "extracted")
SENTENCES_DIR = os.path.join(DATA_DIR, "sentences")


def generate_language_corpus(lang_code: str, max_articles: int):

    lang_pdf_dir = os.path.join(PDFS_DIR, lang_code)
    lang_extracted_dir = os.path.join(EXTRACTED_DIR, lang_code)
    lang_sentences_dir = os.path.join(SENTENCES_DIR, lang_code)

    for dir_path in [lang_pdf_dir, lang_extracted_dir, lang_sentences_dir]:
        os.makedirs(dir_path, exist_ok=True)

    openalex_downloader = OpenAlexDownloader(METADATA_DIR)
    openalex_downloader.download_articles(lang_code, max_articles)

    pdf_processor = PDFProcessor(METADATA_DIR, lang_pdf_dir)
    pdf_processor.download_pdfs(lang_code)


if __name__ == "__main__":

    for dir_path in [DATA_DIR, METADATA_DIR, PDFS_DIR, EXTRACTED_DIR, SENTENCES_DIR]:
        os.makedirs(dir_path, exist_ok=True)

    generate_language_corpus(lang_code="ta", max_articles=10)
