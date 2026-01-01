"""
Sentence Statistics Analyzer

This script analyzes JSONL sentence files to generate comprehensive statistics
including sentence length distributions, duplicate detection, and language-specific metrics.
"""

import os
import json
import pandas as pd
from collections import Counter, defaultdict
from tqdm import tqdm
from utils import load_config


def calculate_stats(sentences_data):
    """Calculate statistics for a list of sentences."""
    lengths = [len(s) for s in sentences_data]
    word_counts = [len(s.split()) for s in sentences_data]

    return {
        "total": len(sentences_data),
        "avg_length": sum(lengths) / len(lengths) if lengths else 0,
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
        "avg_words": sum(word_counts) / len(word_counts) if word_counts else 0,
        "min_words": min(word_counts) if word_counts else 0,
        "max_words": max(word_counts) if word_counts else 0,
    }


def find_duplicates(sentences_data):
    """Find duplicate sentences and return statistics."""
    sentence_counts = Counter(sentences_data)
    duplicates = {s: c for s, c in sentence_counts.items() if c > 1}

    total_duplicates = sum(c - 1 for c in duplicates.values())
    unique_duplicates = len(duplicates)

    return {
        "total_duplicate_instances": total_duplicates,
        "unique_duplicate_sentences": unique_duplicates,
        "duplicate_percentage": (total_duplicates / len(sentences_data) * 100)
        if sentences_data
        else 0,
    }


def analyze_sentence_distribution(sentences_data):
    """Analyze sentence length distribution in bins."""
    lengths = [len(s) for s in sentences_data]

    bins = {"0-50": 0, "51-100": 0, "101-200": 0, "201-300": 0, "301-400": 0, "401+": 0}

    for length in lengths:
        if length <= 50:
            bins["0-50"] += 1
        elif length <= 100:
            bins["51-100"] += 1
        elif length <= 200:
            bins["101-200"] += 1
        elif length <= 300:
            bins["201-300"] += 1
        elif length <= 400:
            bins["301-400"] += 1
        else:
            bins["401+"] += 1

    return bins


def main():
    config = load_config()
    sents_dir = config["directory"]["SENTENCES_DIR"]

    if not os.path.exists(sents_dir):
        print(f"Error: Sentences directory not found: {sents_dir}")
        return

    all_stats = []
    global_sentences = []
    lang_sentences = defaultdict(list)

    print("=" * 80)
    print("SENTENCE STATISTICS ANALYZER")
    print("=" * 80)

    # Read all JSONL files
    jsonl_files = [f for f in os.listdir(sents_dir) if f.endswith(".jsonl")]

    if not jsonl_files:
        print(f"No JSONL files found in {sents_dir}")
        return

    print(f"\nFound {len(jsonl_files)} JSONL file(s)\n")

    for jsonl_file in tqdm(
        jsonl_files,
        desc="Reading sentence files",
        bar_format=config.get(
            "PROGRESS_BAR_FORMAT", "{l_bar}{bar}| {n_fmt}/{total_fmt}"
        ),
    ):
        lang_code = jsonl_file.replace("_sentences.jsonl", "")
        file_path = os.path.join(sents_dir, jsonl_file)

        sentences = []
        doc_ids = set()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        sentences.append(data["text"])
                        doc_ids.add(data["doc_id"])
                        global_sentences.append(data["text"])
                        lang_sentences[lang_code].append(data["text"])

            # Calculate stats for this language
            stats = calculate_stats(sentences)
            dup_stats = find_duplicates(sentences)

            lang_name = config["LANGUAGES"].get(lang_code, {}).get("name", lang_code)

            all_stats.append(
                {
                    "Language": lang_name,
                    "Code": lang_code,
                    "Sentences": stats["total"],
                    "Documents": len(doc_ids),
                    "Avg Len": f"{stats['avg_length']:.1f}",
                    "Avg Words": f"{stats['avg_words']:.1f}",
                    "Duplicates": dup_stats["unique_duplicate_sentences"],
                    "Dup %": f"{dup_stats['duplicate_percentage']:.2f}%",
                }
            )

        except Exception as e:
            print(f"Error processing {jsonl_file}: {str(e)}")

    # Print summary table
    print("\n" + "=" * 80)
    print("LANGUAGE-SPECIFIC STATISTICS")
    print("=" * 80)
    df = pd.DataFrame(all_stats)
    print(df.to_string(index=False))

    # Print detailed statistics for each language
    print("\n" + "=" * 80)
    print("DETAILED STATISTICS BY LANGUAGE")
    print("=" * 80)

    for lang_code, sentences in lang_sentences.items():
        lang_name = config["LANGUAGES"].get(lang_code, {}).get("name", lang_code)
        print(f"\n{lang_name} ({lang_code}):")
        print("-" * 40)

        stats = calculate_stats(sentences)
        dup_stats = find_duplicates(sentences)
        distribution = analyze_sentence_distribution(sentences)

        print(f"  Total Sentences: {stats['total']:,}")
        print(f"  Average Length: {stats['avg_length']:.1f} characters")
        print(f"  Length Range: {stats['min_length']}-{stats['max_length']} characters")
        print(f"  Average Words: {stats['avg_words']:.1f} words")
        print(f"  Word Range: {stats['min_words']}-{stats['max_words']} words")
        print(
            f"  Unique Duplicate Sentences: {dup_stats['unique_duplicate_sentences']:,}"
        )
        print(
            f"  Total Duplicate Instances: {dup_stats['total_duplicate_instances']:,}"
        )
        print(f"  Duplicate Percentage: {dup_stats['duplicate_percentage']:.2f}%")

        print("\n  Length Distribution:")
        for bin_range, count in distribution.items():
            percentage = (count / len(sentences) * 100) if sentences else 0
            print(f"    {bin_range:>10} chars: {count:>6} ({percentage:>5.1f}%)")

    # Print global statistics
    if global_sentences:
        print("\n" + "=" * 80)
        print("GLOBAL STATISTICS (ALL LANGUAGES)")
        print("=" * 80)

        global_stats = calculate_stats(global_sentences)
        global_dup_stats = find_duplicates(global_sentences)
        global_distribution = analyze_sentence_distribution(global_sentences)

        print(f"  Total Sentences: {global_stats['total']:,}")
        print(f"  Average Length: {global_stats['avg_length']:.1f} characters")
        print(
            f"  Length Range: {global_stats['min_length']}-{global_stats['max_length']} characters"
        )
        print(f"  Average Words: {global_stats['avg_words']:.1f} words")
        print(
            f"  Word Range: {global_stats['min_words']}-{global_stats['max_words']} words"
        )
        print(
            f"  Unique Duplicate Sentences: {global_dup_stats['unique_duplicate_sentences']:,}"
        )
        print(
            f"  Total Duplicate Instances: {global_dup_stats['total_duplicate_instances']:,}"
        )
        print(
            f"  Duplicate Percentage: {global_dup_stats['duplicate_percentage']:.2f}%"
        )

        print("\n  Length Distribution:")
        for bin_range, count in global_distribution.items():
            percentage = count / len(global_sentences) * 100
            print(f"    {bin_range:>10} chars: {count:>6} ({percentage:>5.1f}%)")

    print("\n" + "=" * 80)
