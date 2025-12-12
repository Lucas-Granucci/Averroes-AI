import pandas as pd
from pathlib import Path
from data_collection.pipeline import LanguageCorpusCollector
from data_collection.config import LANGUAGES, RESULTS_DIR, ensure_directories


def main():
    # Setup directories
    ensure_directories()

    # Collect corpus for each language
    all_corpus_stats = []

    for lang_code, config in LANGUAGES.items():
        print(f"Processing {config['name']} ({lang_code})")

        collector = LanguageCorpusCollector(
            lang_code=lang_code,
            lang_name=config["name"],
            target_sentences=config["target_sentences"],
            max_articles=config["max_articles"],
        )

        try:
            print("starting collect")
            stats = collector.collect()
            all_corpus_stats.append(stats)
            print(f"\n✓ Completed {config['name']}")
            print(f"  Articles kept: {stats['Articles Kept']}")
        except Exception as e:
            print(f"\n✗ Error collecting {config['name']}: {str(e)}")
            continue


if __name__ == "__main__":
    main()
