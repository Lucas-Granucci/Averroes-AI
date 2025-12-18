from nbclient import NotebookClient
from nbformat import read, write, NO_CONVERT
from pathlib import Path


def run_notebook(input_path: Path, output_path: Path = None, timeout: int = 600):
    if not input_path.exists():
        raise FileNotFoundError(f"Notebook not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        nb = read(f, as_version=NO_CONVERT)

    client = NotebookClient(nb, timeout=timeout, kernel_name="python3")
    client.execute()

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            write(nb, f)


if __name__ == "__main__":
    notebook_paths = [
        "1.0_ObjectiveSetup.ipynb",
        "1.1_MetadataCollection.ipynb",
        "1.2_PDF_Download.ipynb",
        "1.3_Convert_PDFs.ipynb",
        "1.4_SentenceExtraction.ipynb",
        "1.5_BackTranslation.ipynb",
        "1.6_FinalProcessing.ipynb",
    ]

    for notebook_path in notebook_paths:
        run_notebook(Path(notebook_path))
