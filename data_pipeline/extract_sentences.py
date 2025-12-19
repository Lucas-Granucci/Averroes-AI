"""
Sentence Extraction

This script extracts sentences from markdown documents using spaCy.
It cleans and validates sentences, performs language verification,
and saves valid sentences in JSONL format.
"""

import re
import json
import spacy
import pandas as pd
from pathlib import Path
from utils import load_config
from tqdm import tqdm
from lingua import LanguageDetectorBuilder


def detect_language(text: str, detector):
    """Detect the language of the given text."""
    result = detector.detect_language_of(text)
    return result.iso_code_639_1.name.lower() if result else None


def clean_sentence(sentence: str):
    """Clean markdown formatting from sentence."""
    sentence = re.sub(r"\s+", " ", sentence)
    sentence = re.sub(r"#+\s*", "", sentence)
    sentence = re.sub(r"\*+", "", sentence)
    sentence = re.sub(r"\[|\]|\(|\)", "", sentence)
    return sentence.strip()


def is_valid_sentence(sentence: str, min_length: int = 10, max_length: int = 500):
    """Check if sentence meets validity criteria."""
    if len(sentence) < min_length:
        return False
    if len(sentence) > max_length:
        return False
    if not re.search(r"[a-zA-Z\u0080-\uFFFF]", sentence):
        return False
    if len(re.findall(r"[a-zA-Z\u0080-\uFFFF]", sentence)) < 5:
        return False
    return True


def main():
    config = load_config()
    extraction_stats = []

    nlp = spacy.load("xx_ent_wiki_sm")
    nlp.add_pipe("sentencizer")
    detector = LanguageDetectorBuilder.from_all_languages().build()

    for lang_code, lang_config in config["LANGUAGES"].items():
        sents_dir = config["directory"]["SENTENCES_DIR"]
        lang_sents_file = sents_dir / f"{lang_code}_sentences.jsonl"
        lang_extracted_dir = config["directory"]["EXTRACTED_DIR"] / lang_code

        if not lang_extracted_dir.exists():
            continue

        markdown_files = list(lang_extracted_dir.glob("*.md"))
        total_sentences = 0

        with open(lang_sents_file, "w", encoding="utf-8") as out_file:
            for markdown_path in tqdm(
                markdown_files,
                total=len(markdown_files),
                desc=f"Extracting {lang_config['name']}",
                bar_format=config["PROGRESS_BAR_FORMAT"],
            ):
                try:
                    md_text = markdown_path.read_text(encoding="utf-8")

                    # Clean markdown text
                    md_text = re.sub(r"```.*?```", "", md_text, flags=re.DOTALL)
                    md_text = re.sub(r"\|.*?\|", "", md_text)
                    md_text = re.sub(
                        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                        "",
                        md_text,
                    )

                    # Extract sentences
                    doc = nlp(md_text)

                    sentences = []
                    for sent in doc.sents:
                        cleaned = clean_sentence(sent.text)
                        detected_code = detect_language(cleaned, detector)
                        if is_valid_sentence(cleaned) and detected_code == lang_code:
                            sentences.append(cleaned)

                    # Save valid sentences
                    for idx, sentence in enumerate(sentences):
                        data = {
                            "text": sentence,
                            "lang": lang_code,
                            "doc_id": markdown_path.stem,
                            "sent_id": idx,
                        }
                        out_file.write(json.dumps(data, ensure_ascii=False) + "\n")
                        total_sentences += 1

                        if total_sentences >= lang_config["target_sentences"]:
                            break

                except Exception as e:
                    print(f"Error when extracting sentences: {str(e)}")

                if total_sentences >= lang_config["target_sentences"]:
                    break

        extraction_stats.append(
            {
                "Language": lang_config["name"],
                "Code": lang_code,
                "Documents": len(markdown_files),
                "Sentences": total_sentences,
                "Avg per Doc": (
                    f"{total_sentences / len(markdown_files):.1f}"
                    if markdown_files
                    else "0"
                ),
            }
        )

    print("\nSentence Extraction Summary:")
    print(pd.DataFrame(extraction_stats))
