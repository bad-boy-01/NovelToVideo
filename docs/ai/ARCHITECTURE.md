# Architecture

## Components

### Orchestrator
- **`main.py`**: The central controller. Contains a 23-stage sequential execution array. Supports `--resume` flag to safely pick up from crashed states without dropping data.

### The LLM Load Balancer (`app/generators/llm_client.py`)
Because the factory relies on 100% free AI models, it combats API Roulette via:
- **Provider Agnostic**: Native support for OpenRouter.
- **Round-Robin Fallback**: Dynamically catches HTTP 429, 413, 400, and 404 errors and hot-swaps the underlying model endpoint.
- **Truncation Protection**: Traps `json.JSONDecodeError` to identify when a model hit its output `max_tokens` limit, triggering an immediate fallback rather than crashing the pipeline.

### Data Flow
- Pipeline stages DO NOT pass data in memory.
- Stage $N$ writes a JSON or text file to `projects/{project_name}/...`
- Stage $N+1$ reads that file.
- This decoupled nature enables the `--resume` functionality and allows individual stages to be debugged in isolation.

## Project Folders
- `app/pipeline/`: Contains the logic for all 23 distinct stages.
- `app/generators/`: Contains the abstracted LLM and Image Gen clients.
- `projects/`: The isolated working directory for active novels. Contains subfolders for `chunks/`, `scenes/`, `memory/`, `images/`, and `audio/`.
- `configs/`: YAML configuration defining local and LLM strategies.
