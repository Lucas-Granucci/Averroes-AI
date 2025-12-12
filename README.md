# Averroes AI

LLM-based scientific translation for low-resource languages

## Data/Languages

Thai, Tamil, Hebrew, Bengali

## Setup

### 1. Clone repository

```bash
git clone https://github.com/Lucas-Granucci/Averroes-AI.git
cd Averroes-AI
```

### 2. Activate virtual environment

```bash
py -3.11 -m venv venv
```

```bash
venv\Scripts\activate      # Windows
source venv/bin/activate   # MacOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130
```

```bash
pip3 install jupyter notebook ipykernel pymupdf pandas tqdm matplotlib ipython pymupdf4llm lingua-language-detector requests selenium spacy seaborn openai
```

```bash
python -m spacy download xx_ent_wiki_sm
```