"""
Final Processing

TODO:
1. Trim all datasets to equal length
2. Split into train/test/val with appropriate ratios
"""

import os
import json
from utils import load_config
from sklearn.model_selection import train_test_split


def main():
    config = load_config()

    for lang_code, lang_config in config["LANGUAGES"].items():
        parallel_data_dir = config["directory"]["PARALLEL_DATA_DIR"]
        parallel_sents_file = f"{parallel_data_dir}/{lang_code}-en_data.jsonl"

        if not os.path.exists(parallel_sents_file):
            continue

        with open(parallel_sents_file, "r", encoding="utf-8") as f:
            paralell_sents = [json.loads(line) for line in f]

        num_sents = len(paralell_sents)
        target_sents = lang_config["target_sentences"]

        print(
            f"Created {num_sents} parallel sentence pairs of {target_sents} target pairs"
        )

        val_ratio = config["data_processing"]["train_val_test_split"]["val_ratio"]
        test_ratio = config["data_processing"]["train_val_test_split"]["val_ratio"]
        temp_ratio = val_ratio + test_ratio
        seed = config["project"]["seed"]

        train, temp = train_test_split(
            paralell_sents, test_size=temp_ratio, random_state=seed
        )
        val, test = train_test_split(
            temp, test_size=test_ratio / temp_ratio, random_state=seed
        )

        # Save splits
        for split_name, split_data in [("train", train), ("val", val), ("test", test)]:
            output_file = f"{parallel_data_dir}/{lang_code}-en_{split_name}.jsonl"
            with open(output_file, "w", encoding="utf-8") as f:
                for item in split_data:
                    f.write(json.dumps(item) + "\n")

    print("\nParallel Corpus Split:")
