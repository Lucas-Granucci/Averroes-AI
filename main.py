"""
Main Pipeline Runner

Edit SCRIPTS_TO_RUN below to select which scripts to execute.
"""

from data_pipeline import (
    setup,
    collect_metadata,
    convert_pdfs,
    download_pdfs,
    extract_sentences,
    generate_statistics,
    backtranslate,
    # finalize_corpus,
)


def build_corpus():
    print("Generating corpus")
    # setup.main()
    # collect_metadata.main()
    # download_pdfs.main()
    # convert_pdfs.main()
    # extract_sentences.main()
    backtranslate.main()
    # finalize_corpus.main()


def analyze():
    generate_statistics.main()


if __name__ == "__main__":
    build_corpus()
    # analyze()
