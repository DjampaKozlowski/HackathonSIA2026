# HackathonSIA2026

# Setup

## I. LM-studio
LM-studio allow to run local LLM locally. LM-studio provides a clean GUI to download, manage, and interact with LLM. It also can be used as a server that can be accessed though API or dedicated SDK. 

### I-1. install lm-studio
Download and install LM-studio from the followsing adress : https://lmstudio.ai/

### I-2. add models
from LM-studio, install the following models:

```bash
# Computer vision & LLM
google/gemma-2-12b
# Embedding
nomic-embed-text-v1.5
```

## II. `uv`

### 1. install `uv`
uv is a package and environment manager. Install uv with the standalone installers 

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
if not working, see [official doc](https://docs.astral.sh/uv/getting-started/installation/)

### 2. create a virtual environment (local)

```bash
# From the HackathonSIA2026 directory
uv venv
```

### 3. install dependencies listed in the `pyproject.toml`file

```bash
uv sync
```
---

# Other infos 

## Embedding 

Scores d'embedding (nomic-embed-text-v1.5)

| Score cosine | Interprétation         |
| ------------ | ---------------------- |
| > 0.85       | quasi équivalent       |
| 0.75–0.85    | très proche            |
| 0.65–0.75    | proche                 |
| 0.50–0.65    | relation faible        |
| < 0.50       | probablement différent |

# TODO

- [ ] Remove aliases ? 

# Run API
run : `uv run fastapi dev ./api.py`
