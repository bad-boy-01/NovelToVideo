# Architectural Decisions

This file tracks major shifts in the pipeline's logic to prevent future regressions.

## 2026-06-10: The Great OpenRouter Migration
- **Decision**: Abandoned the `google.generativeai` SDK entirely. Switched to `openai` python package pointing to OpenRouter.
- **Reason**: The Google Free Tier enforces a strict 20-request/day limit, which is physically impossible to bypass for massive novels.
- **Impact**: All pipeline stages now instantiate `LLMClient` instead of `GeminiClient`.

## 2026-06-10: The Fallback Load-Balancer
- **Decision**: Implemented an auto-router inside `llm_client.py` that cycles through an array of `FALLBACK_MODELS`.
- **Reason**: The `openrouter/free` meta-endpoint and other free models constantly throw 429 (Rate Limit), 413 (Payload Too Large), and 404 (Decommissioned) errors. The router catches these and hot-swaps to the next model.
- **Impact**: Zero pipeline crashes due to temporary free-tier server outages.

## 2026-06-10: Centralized JSON Cutoff Protection
- **Decision**: Moved the `json.loads()` validation inside the `llm_client.py` retry loop.
- **Reason**: Small free-tier models (or models explicitly clamped by `max_tokens`) frequently cut off mid-sentence, returning an Unterminated String. Previously, this crashed the specific Stage attempting to parse it. Now, it triggers the Auto-Router to switch to a higher-capacity model.
- **Impact**: Hard requirement that NO stage attempts to manually repair broken JSON. The `LLMClient` must guarantee complete JSON before returning.
