# AI Memory Core: AGENTS.md

Welcome to the `manhwa-video-factory` project. This document serves as the persistent memory system and operational boundary for all AI agents working on this codebase.

## 1. Project Overview
This factory automates the generation of dynamic Manhwa-style recap videos from raw text novels. It uses an asynchronous 23-stage pipeline orchestrated by `main.py` that handles text chunking, character extraction, World/Style Bible generation, scene-by-scene Image Generation (Flux/SDXL via Kaggle GPUs), TTS Voice Generation, and final FFmpeg assembly.

## 2. Technology Stack
- **Core:** Python 3.11+
- **LLM/Extraction:** OpenRouter (`openrouter/free` meta-endpoint, `qwen3`, `llama4`, `deepseek`)
- **Image Generation:** Stable Diffusion XL / Flux-dev via ComfyUI local pipelines
- **TTS:** Kokoro TTS
- **Assembly:** FFmpeg

## 3. Architecture Philosophy
The pipeline is strictly modular. Data is passed between stages via JSON files and text files generated in the `projects/{project_name}/` directory. The memory system relies heavily on `character_registry.json`.

## 4. Hard Rules for AI Agents
1. **Always Read `docs/ai/`**: Before executing code changes, read the relevant context in `docs/ai/`.
2. **Update the Memory**: Upon completing a task or milestone, you MUST update `docs/ai/PROJECT_STATUS.md`, `docs/ai/TASKS.md`, `docs/ai/CHANGELOG.md`, and `docs/ai/DECISIONS.md`.
3. **Never Redesign Architecture Arbitrarily**: Structural changes require explicit user authorization.
4. **Kaggle Environment Constraints**: This pipeline runs heavily on Kaggle (2x T4 GPUs). Code must be fully compatible with Kaggle notebooks and avoid requiring interactive CLI inputs.
5. **Character Consistency is King**: The character registry is the most critical asset. Never overwrite it without extreme confidence checks.
6. **No API Roulette Crashes**: Always ensure JSON parsers are wrapped in robust `try/except` loops to catch Free-Tier token limits and trigger LLM Auto-Routers.

*End of Core Directive. Consult `docs/ai/PROJECT_CONTEXT.md` to begin.*
