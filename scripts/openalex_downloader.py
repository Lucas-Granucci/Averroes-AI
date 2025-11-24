import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from requests.adapters import HTTPAdapter, Retry


class OpenAlexDownloader:
    def __init__(self, data_dir: str):
        """Initialize Openalex database downloader"""
        self.session = self._create_session()
        self.data_dir = data_dir

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

    def _validate_url(self, pdf_url: str) -> bool:
        """Validate PDF url exists"""
        try:
            response = self.session.head(pdf_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _extract_pdf_url(self, api_result: str) -> str:
        """Extract the PDF url from an OpenAlex entry"""
        primary_location = api_result["primary_location"]
        pdf_url = primary_location.get("pdf_url", "")
        return pdf_url

    def _reconstruct_abstract(self, abstract_inverted_index: dict) -> str:
        """Reconstruct abstract from inverted index"""
        if not abstract_inverted_index:
            return ""

        word_indeces = []
        for word, indeces in abstract_inverted_index.items():
            word_indeces.extend([(idx, word) for idx in indeces])

        sorted_indeces = sorted(word_indeces, key=lambda x: x[0])
        return " ".join([index[1] for index in sorted_indeces])

    def download_articles(self, lang_code: str, max_articles: int) -> pd.DataFrame:
        """Collect article URLS from OpenAlex database with valid PDFs and asbracts"""

        # Parameters
        url = "https://api.openalex.org/works"

        filters = [f"language:{lang_code}", "type:article"]
        fields = [
            "abstract_inverted_index",
            "primary_location",
            "title",
            "doi",
            "publication_date",
        ]

        params = {
            "filter": ",".join(filters),
            "select": ",".join(fields),
            "mailto": "example@email.com",
            "page": 1,
        }

        # Indexing variables
        has_more_pages = True
        reached_num_articles = False

        article_data = []
        total_articles = 0

        pbar = tqdm(total=max_articles, desc=f"Collecting {lang_code} articles")

        # Page through OpenAlex database and collect article metadata
        while has_more_pages and not reached_num_articles:
            response = self.session.get(url, params=params)
            page_with_results = response.json()
            results = page_with_results["results"]

            for api_result in results:
                pdf_url = self._extract_pdf_url(api_result)
                abstract = self._reconstruct_abstract(
                    api_result["abstract_inverted_index"]
                )

                if not pdf_url:
                    continue

                article_data.append(
                    {
                        "title": api_result["title"],
                        "abstract": abstract,
                        "pdf_url": pdf_url,
                        "doi": api_result["doi"],
                        "publication_date": api_result["publication_date"],
                    }
                )

                pbar.update(1)
                total_articles += 1
                if total_articles >= max_articles:
                    break

            params["page"] += 1

            per_page = page_with_results["meta"]["per_page"]
            has_more_pages = len(results) == per_page
            reached_num_articles = total_articles >= max_articles
            time.sleep(4)

        article_df = pd.DataFrame(article_data)
        file_name = f"{lang_code}_article_data.csv"
        article_df.to_csv(os.path.join(self.data_dir, file_name), encoding="utf-8")
        return article_df
