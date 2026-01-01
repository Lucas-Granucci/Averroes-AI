"""
Final Processing

TODO:
1. Trim all datasets to equal length
2. Split into train/test/val with appropriate ratios
"""

import os
import pandas as pd
from utils import load_config


def main():
    config = load_config()
    finalizing_stats = []

    for lang_code, lang_config in config["LANGUAGES"].items():
        parallel_data_dir = config["directory"]["PARALLEL_DATA_DIR"]
        parallel_sents_file = f"{parallel_data_dir}/{lang_code}-en_data.jsonl"

        if not os.path.exists(parallel_sents_file):
            continue

        finalizing_stats.append(
            {
                "Language": lang_config["name"],
                "Code": lang_code,
            }
        )

    print("\nParallel Corpus Summary:")
    print(pd.DataFrame(finalizing_stats))
