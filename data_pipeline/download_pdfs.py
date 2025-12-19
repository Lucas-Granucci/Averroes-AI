"""
PDF Download

This script downloads PDF files from the URLs collected in the metadata.
It uses Selenium WebDriver with headless Chrome to download PDFs for each language.
"""

import time
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from utils import load_config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def setup_pdf_driver(download_dir: Path):
    """Configure Chrome WebDriver for PDF downloads."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "plugins.plugins_disabled": ["Chrome PDF Viewer"],
        },
    )
    return webdriver.Chrome(options=options)


def download_pdf(driver, pdf_url: str):
    """Download a single PDF using Selenium."""
    driver.get(pdf_url)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(5)


def main():
    config = load_config()
    download_stats = []

    for lang_code, lang_config in config["LANGUAGES"].items():
        lang_pdf_dir = config["directory"]["PDFS_DIR"] / lang_code
        lang_pdf_dir.mkdir(parents=True, exist_ok=True)

        # Load metadata
        metadata_dir = config["directory"]["METADATA_DIR"]
        metadata_path = metadata_dir / f"{lang_code}_article_data.csv"
        if not metadata_path.exists():
            print(f"No metadata found for {lang_code}, skipping")
            continue

        articles_df = pd.read_csv(metadata_path)
        driver = setup_pdf_driver(lang_pdf_dir)

        # Download PDFs
        success_count = 0
        for _, article in tqdm(
            articles_df.iterrows(),
            total=len(articles_df),
            desc=f"Downloading {lang_config['name']}",
            bar_format=config["PROGRESS_BAR_FORMAT"],
        ):
            try:
                download_pdf(driver, article["pdf_url"])
                success_count += 1
            except Exception:
                pass

        driver.quit()

        download_stats.append(
            {
                "Language": lang_config["name"],
                "Attempted": len(articles_df),
                "Downloaded": success_count,
                "Success Rate": (
                    f"{success_count / len(articles_df) * 100:.1f}%"
                    if len(articles_df) > 0
                    else "0%"
                ),
            }
        )

    print("\nPDF Download Summary:")
    print(pd.DataFrame(download_stats))
