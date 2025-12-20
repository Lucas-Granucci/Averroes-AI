"""
Back Translation

This script creates parallel data by translating sentences from target languages
to English using OpenAI's Batch API. It generates batch query files, submits them
for processing, and formats the results into parallel corpus files.
"""

import os
import json
import time
from openai import OpenAI
from utils import load_config
from dotenv import load_dotenv


def create_translation_prompt(sentence: str, lang_name: str) -> str:
    """Create a translation prompt for the given sentence."""
    return f"Translate the following {lang_name} sentence into English:\n{sentence}"


def create_batch_query_files(config: dict) -> None:
    sents_dir = config["directory"]["SENTENCES_DIR"]
    api_queries_dir = config["directory"]["API_QUERIES_DIR"]

    api_url = "/v1/chat/completions"
    model = config["data_processing"]["back_translation"]["model"]
    system_prompt = config["data_processing"]["back_translation"]["system_prompt"]
    max_tokens = config["data_processing"]["back_translation"]["max_tokens"]

    for lang_code, lang_config in config["LANGUAGES"].items():
        lang_sents_file = f"{sents_dir}/{lang_code}_sentences.jsonl"
        lang_queries_file = f"{api_queries_dir}/{lang_code}_queries.jsonl"

        with open(lang_sents_file, "r", encoding="utf-8") as file:
            lang_sents = [json.loads(line) for line in file]

        if not lang_sents:
            continue

        with open(lang_queries_file, "w", encoding="utf-8") as out_file:
            for idx, sent in enumerate(lang_sents):
                query_id = f"{lang_code}_{idx}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": create_translation_prompt(
                            sent["text"], lang_config["name"]
                        ),
                    },
                ]
                query = {
                    "custom_id": query_id,
                    "method": "POST",
                    "url": api_url,
                    "body": {
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                    },
                }
                out_file.write(json.dumps(query, ensure_ascii=False) + "\n")

    print("Batch query files created successfully!")


def submit_batch_jobs(config: dict, client: OpenAI) -> dict:
    api_queries_dir = config["directory"]["API_QUERIES_DIR"]
    batch_info = {}

    for lang_code, _ in config["LANGUAGES"].items():
        lang_queries_file = f"{api_queries_dir}/{lang_code}_queries.jsonl"

        if not os.path.exists(lang_queries_file):
            continue

        # Upload file
        batch_input_file = client.files.create(
            file=open(lang_queries_file, "rb"), purpose="batch"
        )

        # Create batch job
        batch = client.batches.create(
            input_file_id=batch_input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": f"backtranslation batch for {lang_code}"},
        )
        batch_info[lang_code] = batch
        print(f"Submitted batch for {lang_code}: {batch.id}")

    print(f"\nSubmitted {len(batch_info)} batch jobs successfully!")
    return batch_info


def check_batch_status(client: OpenAI, batch_info: dict) -> dict:
    for key, batch in batch_info.items():
        batch = client.batches.retrieve(batch.id)
        batch_info[key] = batch
        counts = batch.request_counts
        print(
            f"{key}: status={batch.status}, completed={counts.completed}, failed={counts.failed}, total={counts.total}"
        )

    return batch_info


def retrieve_and_create_parallel_data(
    config: dict, client: OpenAI, batch_info: dict
) -> None:
    """Step 4: Retrieve results and create parallel data files."""

    sents_dir = config["directory"]["SENTENCES_DIR"]
    parallel_data_dir = config["directory"]["PARALLEL_DATA_DIR"]

    # Retrieve batch responses
    batch_responses = {}
    for key, batch in batch_info.items():
        if batch.output_file_id:
            file_response = client.files.content(batch.output_file_id)
            batch_responses[key] = [
                json.loads(res) for res in file_response.text.split("\n") if res
            ]

    # Create parallel data files
    for lang_code, _ in config["LANGUAGES"].items():
        lang_sents_file = f"{sents_dir}/{lang_code}_sentences.jsonl"
        parallel_sents_file = f"{parallel_data_dir}/{lang_code}-en_data.jsonl"

        with open(lang_sents_file, "r", encoding="utf-8") as file:
            lang_sents = [json.loads(line) for line in file]

        if not lang_sents:
            continue

        if lang_code not in batch_responses.keys():
            continue

        # Extract translations
        translated_sentences = [
            res["response"]["body"]["choices"][0]["message"]["content"]
            for res in batch_responses[lang_code]
        ]

        assert len(translated_sentences) == len(lang_sents), (
            f"Mismatch: {len(translated_sentences)} translations vs {len(lang_sents)} source sentences"
        )

        # Write parallel data
        with open(parallel_sents_file, "w", encoding="utf-8") as outfile:
            for target, source in zip(lang_sents, translated_sentences):
                outfile.write(
                    json.dumps(
                        {
                            "target_text": target["text"],
                            "target_lang": lang_code,
                            "source_text": source,
                            "source_lang": "en",
                            "doc_id": target["doc_id"],
                            "sent_id": target["sent_id"],
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        print(
            f"Created parallel data for {lang_code}: {len(translated_sentences)} sentence pairs"
        )

    print("\nParallel data creation complete!")


def main():
    load_dotenv()
    config = load_config()

    create_batch_query_files(config)

    client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))
    batch_info = submit_batch_jobs(config, client)

    done = False
    while not done:
        batch_info = check_batch_status(client, batch_info)
        statuses = [batch.status for _, batch in batch_info.items()]
        done = all(batch == "completed" for batch in statuses)
        time.sleep(30)

    retrieve_and_create_parallel_data(config, client, batch_info)
