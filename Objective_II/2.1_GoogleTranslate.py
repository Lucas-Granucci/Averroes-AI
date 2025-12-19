"""
Google Translate Translation

Free translation using translate.google.com
"""

import yaml
import json
from pathlib import Path
from googletrans import Translator


def main():
    """Translate sentences using Google Translate."""
    # Load configuration
    with open("../config.yaml") as f:
        config = yaml.safe_load(f)

    # Set up project paths
    project_root = Path.cwd().parent
    PARALLEL_DATA_DIR = project_root / config["PARALLEL_DATA_DIR"]

    translator = Translator()

    for lang_code, lang_config in config["LANGUAGES"].items():
        parallel_sents_file = PARALLEL_DATA_DIR / f"{lang_code}-en_data.jsonl"

        if not parallel_sents_file.exists():
            print(f"No parallel data file found for {lang_code}, skipping")
            continue

        with open(parallel_sents_file, "r", encoding="utf-8") as file:
            sentences = [json.loads(line) for line in file]

        if not sentences:
            continue

        print(f"Translating {len(sentences)} sentences for {lang_code}...")

        # Add translation logic here
        print(f"Completed translation for {lang_code}")


if __name__ == "__main__":
    main()
