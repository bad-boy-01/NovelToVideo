import json
import re
from pathlib import Path
from app.generators.gemini_client import GeminiClient
from app.utils.logger import logger

class Stage04WorldBible:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.chunks_dir = project_path / "chunks"
        self.memory_dir = project_path / "memory"
        self.world_bible_path = self.memory_dir / "world_bible.json"
        self.gemini = GeminiClient()
        
    def _clean_json_response(self, text: str) -> dict:
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        return json.loads(cleaned.strip())
        
    def run(self):
        logger.info("Executing Stage 04: World Bible Generation")
        
        chunk_files = sorted(list(self.chunks_dir.glob("chunk_*.txt")))
        if not chunk_files:
            raise FileNotFoundError("No chunks found. Run Stage 02 first.")
            
        current_world = {}
        if self.world_bible_path.exists():
            with open(self.world_bible_path, "r", encoding="utf-8") as f:
                current_world = json.load(f)
                
        for chunk_file in chunk_files:
            logger.info(f"Processing {chunk_file.name} for World lore...")
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_text = f.read()
                
            prompt = (
                "You are an expert World Builder for a Korean Manhwa adaptation.\n"
                "Return a JSON dictionary where keys are specific locations, sects, magical items, or world concepts, and values are detailed visual descriptions.\n"
                f"Current World State:\n{json.dumps(current_world, indent=2)}\n\n"
                "Update the world state with any new locations or concepts found in this chunk. Retain all old concepts exactly as they are."
            )
            
            result_text = self.gemini.generate_json(prompt, chunk_text)
            try:
                current_world = self._clean_json_response(result_text)
                with open(self.world_bible_path, "w", encoding="utf-8") as f:
                    json.dump(current_world, f, indent=2)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini output for {chunk_file.name}: {e}")
                raise
                
        logger.info(f"Stage 04 Complete. World Bible updated.")
