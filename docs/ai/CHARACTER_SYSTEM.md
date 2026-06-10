# Character System

## Overview
Visual consistency across a 1,000-scene video (or multiple sequel videos) is achieved via the `memory/character_registry.json`.

## Mechanism
1. **Initial Discovery**: When `Stage03CharacterBible` encounters a new character name, it assigns them a permanent Canonical Name and extracts their visual "fingerprint" (hair color, clothing, notable features).
2. **Confidence Locking**: If subsequent chunks mention the character vaguely, the LLM will assign a `fingerprint_confidence` < 0.9. The script intercepts this and *protects* the original fingerprint from being overwritten.
3. **Versions**: If a character undergoes a major time-skip or outfit change, a new entry is added to their `versions` array rather than wiping their base identity.
4. **Sequel Support**: Because the registry is saved as an isolated JSON file, future projects can load it during Stage 01 to maintain 100% consistency with previous videos.
