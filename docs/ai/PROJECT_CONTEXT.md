# Project Context

## Purpose
The `manhwa-video-factory` is designed to ingest raw text files (novels or scripts) and autonomously compile them into fully animated, voice-acted, and visually consistent Manhwa-style recap videos for YouTube.

## Workflow
1. **Ingestion**: A user drops a `script.txt` file into a project folder.
2. **Analysis & Memory**: The pipeline chunks the script to bypass LLM context limits. It extracts characters, locations, and artistic styles, building a persistent memory state in `character_registry.json` and `world_bible.json`.
3. **Extraction**: The text is split into cinematic 6-second scenes.
4. **Rendering**: Prompts are dynamically assembled and sent to Kaggle GPUs to render images via SDXL or Flux.
5. **Audio**: Narration is fed into a TTS engine.
6. **Assembly**: FFmpeg stitches the images, audio, dynamic zooms (Ken Burns effect), and subtitles into a final video file.

## Input
- `projects/{project_name}/script.txt`

## Output
- `projects/{project_name}/final_video.mp4`
- Associated thumbnails and SEO metadata packages.

## Constraints & Assumptions
- **Kaggle Infrastructure**: Runs inside a Jupyter notebook environment with T4/L4 GPUs.
- **Free-Tier Limits**: The pipeline must constantly combat and load-balance across free LLM APIs (OpenRouter) using aggressive `max_tokens` handling, rate-limit sleeping, and robust model swapping.
