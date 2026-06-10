import json
import re
from pathlib import Path
from app.generators.gemini_client import GeminiClient
from app.utils.logger import logger

class Stage03CharacterBible:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.chunks_dir = project_path / "chunks"
        self.memory_dir = project_path / "memory"
        self.registry_path = self.memory_dir / "character_registry.json"
        self.gemini = GeminiClient()
        self.prompt_template_path = Path("prompts/bible_prompt.txt")
        
    def _clean_json_response(self, text: str) -> dict:
        """Strips markdown formatting if Gemini forgets to use strict JSON mode."""
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        return json.loads(cleaned.strip())
        
    def run(self):
        logger.info("Executing Stage 03: Character Registry Generation")
        
        if not self.prompt_template_path.exists():
            raise FileNotFoundError("Missing bible_prompt.txt")
            
        with open(self.prompt_template_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()
            
        chunk_files = sorted(list(self.chunks_dir.glob("chunk_*.txt")))
        if not chunk_files:
            raise FileNotFoundError("No chunks found. Run Stage 02 first.")
            
        current_registry = {}
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                current_registry = json.load(f)
                
        for chunk_file in chunk_files:
            logger.info(f"Processing {chunk_file.name} for Character updates...")
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_text = f.read()
                
            prompt = (
                base_prompt + "\n\n"
                "Return a JSON dictionary where keys are character canonical names and values are the CharacterRegistryEntry objects.\n"
                f"Current Registry State:\n{json.dumps(current_registry, indent=2)}\n\n"
                "INSTRUCTIONS:\n"
                "1. If a character already exists, ONLY update their fingerprint if the new chunk explicitly provides clearer details. Rate your confidence in this change via 'fingerprint_confidence' (0.0 to 1.0).\n"
                "2. If 'fingerprint_confidence' < 0.9, set 'needs_review' to true and DO NOT overwrite their main fingerprint.\n"
                "3. If a character experiences a time-skip or major appearance change in this chunk, ADD a new CharacterVersion to their 'versions' array.\n"
                "4. If a completely new character appears in this chunk, CREATE a new entry for them.\n"
                "5. Make sure to return the full, merged registry including all previous characters, even if they didn't appear in this chunk."
            )
            
            result_text = self.gemini.generate_json(prompt, chunk_text)
            try:
                updated_registry = self._clean_json_response(result_text)
                
                # Apply Confidence Lock
                for char_id, entry in updated_registry.items():
                    confidence = entry.get("fingerprint_confidence", 1.0)
                    if confidence < 0.9:
                        entry["needs_review"] = True
                        if char_id in current_registry:
                            entry["fingerprint"] = current_registry[char_id].get("fingerprint")
                            
                current_registry = updated_registry
                
                # Iteratively save progress
                with open(self.registry_path, "w", encoding="utf-8") as f:
                    json.dump(current_registry, f, indent=2)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini output for {chunk_file.name}: {e}")
                raise
                
        logger.info(f"Stage 03 Complete. Registry secured with {len(current_registry)} characters.")
