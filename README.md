# Averroes AI

LLM-based scientific translation for low-resource languages

## Data/Languages

Thai, Tamil, Swahili, Bengali, Estonian

## Setup

### 1. Clone and setup environment

```bash
git clone https://github.com/Lucas-Granucci/Averroes-AI.git
cd Averroes-AI
py -3.11 -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # MacOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130
pip install jupyter notebook ipykernel pymupdf pandas tqdm matplotlib ipython pymupdf4llm lingua-language-detector requests selenium spacy seaborn openai googletrans python-dotenv nbclient nbformat
python -m spacy download xx_ent_wiki_sm
```

### 3. Configure API
Create `.env` file:
```
OPENAI_APIKEY=your_secret_api_key_here
```

## Objective Structure

### Objective I
Develop pipeline for automated parallel corpora creation by downloading monolingual academic documents and backtranslating with SoTA LLMs.

### Objective II
Establish baseline results for translating academic documents into low-resource languages with current gold-standard machine translation models.

### Objective III
Fine-tune LLM using HuggingFace Transformers with studies on optimal prompt structure and in-context learning templates.

### Objective IV
Evaluate fine-tuned LLMs translation performance with automated metrics and compare results to baseline machine translation models.