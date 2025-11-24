import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class PDFDownloader:
    def __init__(self, pdf_dir: str):
        self.pdf_dir = pdf_dir
        self.driver = self._setup_selenium()

    def _setup_selenium(self):
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
                "download.default_directory": self.pdf_dir,  # Download to PDF directory
                "download.prompt_for_download": False,  # Disable download prompt
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True,  # Automatically download PDFs
                "plugins.plugins_disabled": ["Chrome PDF Viewer"],
            },
        )

        driver = webdriver.Chrome(options=options)
        return driver

    def download_pdf(self, pdf_url: str):
        self.driver.get(pdf_url)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(5)

    def __del__(self):
        if hasattr(self, "driver"):
            self.driver.quit()
