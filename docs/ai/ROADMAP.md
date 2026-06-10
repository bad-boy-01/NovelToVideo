# Roadmap

## Phase 1: The Resilient Foundation
Focus on making the text-extraction process 100% immune to API rate limits, model deprecations, and token truncations using free-tier resources. 

## Phase 2: Production Hardening
Introduce telemetry, manual override capabilities, and state snapshots. This phase focuses on stability and debugging tooling for humans.

## Phase 3: The Image Pipeline
Connect the verified Prompt JSONs to the local Kaggle GPU image generator (ComfyUI / Diffusers). Focus on consistency using ControlNet and IP-Adapters.

## Phase 4: Audio-Visual Assembly
Sync timing. Implement dynamic zoom/pan logic inside FFmpeg.

## Phase 5: Automation Scaling
Move away from Free APIs. Implement Paid API integration or Local LLM endpoints to bypass the "Free Tier Roulette" entirely.
