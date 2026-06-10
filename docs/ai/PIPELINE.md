# Pipeline Breakdown

The factory executes exactly 23 deterministic stages via `main.py`.

1. **Stage01Ingestion**: Validates `script.txt` and normalizes encoding.
2. **Stage02Chunker**: Slices massive novels into ~2000-word logical chunks to bypass LLM context limitations.
3. **Stage03CharacterBible**: Incrementally extracts characters, assigning permanent IDs and visual fingerprints.
4. **Stage04WorldBible**: Extracts named locations, establishing lore-accurate establishing shots.
5. **Stage05StyleBible**: Analyzes prose tone to dictate specific ComfyUI visual styles (e.g., "Dark Fantasy", "Romance Glassmorphism").
6. **Stage06ReferenceGen**: Pre-computes reference images for recurring characters to feed into IP-Adapters.
7. **Stage07aSceneExtractor**: Divides chunks into 60-word micro-scenes.
8. **Stage07bSceneValidator**: Ensures JSON structural integrity.
9. **Stage07cCoverageValidator**: Ensures no story beats were skipped.
10. **Stage07dDensityValidator**: Re-chunks if a scene is too long.
11. **Stage08PromptInjector**: Translates story beats into rigid SDXL/Flux positive/negative image prompts.
12. **Stage09ImageGen**: Primary render pass on Kaggle GPUs.
13. **Stage10SceneVerifier**: LLM Vision evaluates generated images for mutations or prompt-drifts.
14. **Stage09bPromptRewriter**: Salvages failed images by re-weighting ComfyUI tags.
15. **Stage09ImageGen**: Secondary fallback render pass.
16. **Stage11TTSGen**: Generates Kokoro voice acting for narration blocks.
17. **Stage12Timeline**: Computes exact duration required for images based on TTS length.
18. **Stage13FFmpegAssembly**: Core video stitcher.
19. **Stage18SubtitleGen**: SRT generation synced to voice.
20. **Stage15SEOGen**: LLM generates optimized YouTube titles and tags.
21. **Stage14ThumbnailGen**: Composes a click-optimized thumbnail.
22. **Stage16YouTubePackage**: Archives outputs into a `.zip`.
23. **Stage17GlobalMemory**: Syncs the isolated `project/memory` up to the global factory index for sequel support.
