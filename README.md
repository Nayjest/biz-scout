## BizScout

A tool that builds a local, queryable knowledge base about a target company from
public sources, then answers questions about it offline.

### How it works

1. **Collect** — public information about the company is gathered online via the
   [Perplexity](https://www.perplexity.ai/) API (`sonar-pro`).
2. **Index** — the collected facts are embedded with a local Ollama model
   (`paraphrase-multilingual`) and stored in a local **ChromaDB** vector store.
3. **Answer** — a local chat LLM (Ollama `qwen3.5:9b`) answers questions against the
   stored knowledge base, using tool calls to index new companies on demand.

The chat/embedding models run fully locally (via Ollama in Docker). Only the initial
data collection step reaches out to Perplexity.

### Prerequisites

- **Docker** + **Docker Compose**.
- An **NVIDIA GPU** with the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
  is recommended (the `ollama` service requests GPU passthrough). Remove the `deploy:`
  block from `docker-compose.yml` to run CPU-only.
- A **Perplexity API key** — get one at https://www.perplexity.ai/settings/api.

### Setup

Data collection requires a Perplexity API key. Copy the example file and fill in your
key:

```powershell
copy .env.example .env.perplexity
```

Then edit `.env.perplexity` and set perplexity API KEY.

### Run (Docker)

```powershell
docker-compose up --build
```

This starts Ollama, pulls and warms the chat + embedding models (first run downloads
~7 GB, so give it a few minutes), then launches the Streamlit UI.

Open **http://localhost:8501** and ask about a company. If it isn't indexed yet, the
assistant offers to collect and build its knowledge base on the fly.

Model selection lives in `.env` (`docker-compose.yml` reads it from there):

```ini
OLLAMA_MODEL=qwen3.5:9b
EMBEDDING_MODEL=paraphrase-multilingual
```

Pulled models persist in `./storage/ollama-models` across restarts.

### Index a company from the CLI

To build the knowledge base for a company without the UI, run `index_company.py`. It
takes the company name as the first argument (defaults to `OBRIO` if omitted):

```powershell
uv run python index_company.py "Microsoft"
```

This collects facts via Perplexity and writes them to the local ChromaDB store, so it
also needs a valid `.env.perplexity`.

### Local development

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (see `pyproject.toml` /
`uv.lock`, Python ≥ 3.10):

```powershell
uv sync            # create the venv and install dependencies
uv run ruff check  # lint
```
