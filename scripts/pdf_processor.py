import os
import time
import fitz
import requests
import pymupdf4llm
import pandas as pd
from tqdm import tqdm
from requests.adapters import HTTPAdapter, Retry


class PDFProcessor:
    def __init__(self, data_dir: str, pdf_dir):
        self.data_dir = data_dir
        self.pdf_dir = pdf_dir
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry logic and connection pooling"""
        session = requests.session()
        retry_strategy = Retry(
            total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _is_text_pdf(self, pdf_path: str) -> bool:
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text = page.get_text()
                if text and text.strip():
                    return True
            return False
        except Exception:
            return False

    def download_pdfs(self, lang_code: str) -> None:
        article_data_path = os.path.join(self.data_dir, f"{lang_code}_article_data.csv")
        article_data = pd.read_csv(article_data_path, encoding="utf-8")

        if article_data.empty:
            print(f"{article_data_path} is empty, no articles found")
            return

        pdf_urls = article_data["pdf_url"].to_list()

        article_idx = 0
        for pdf_url in tqdm(pdf_urls, desc=f"Downloading {lang_code} PDFs"):
            headers = {"User-Agent": "Mozzila/5.0"}

            try:
                response = self.session.get(pdf_url, headers=headers, timeout=10)

                pdf_path = os.path.join(self.pdf_dir, f"{article_idx}.pdf")
                with open(pdf_path, "wb") as file:
                    file.write(response.content)

                if self._is_text_pdf(pdf_path):
                    article_idx += 1
                else:
                    os.remove(pdf_path)

            except requests.exceptions.RequestException:
                pass

        print(f"Successfully downloaded {article_idx} of {len(article_data)} articles")
