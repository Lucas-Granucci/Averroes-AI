"""
Objective I Setup

This script initializes the directory structure for Objective I data processing,
creating folders for metadata, PDFs, extracted text, sentences, API queries,
parallel data, and results.
"""

from pathlib import Path
from utils import load_config


def main():
    config = load_config()

    # Create directories
    for _, dir_path_name in config["directory"].items():
        dir_path = Path.cwd() / dir_path_name
        dir_path.mkdir(parents=True, exist_ok=True)

    print("Directory structure created successfully!")
