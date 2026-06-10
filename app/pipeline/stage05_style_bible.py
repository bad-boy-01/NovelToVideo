import json
import re
from pathlib import Path
from app.generators.gemini_client import GeminiClient
from app.utils.logger import logger

class Stage05StyleBible:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.chunks_dir = project_path / "chunks"
        self.memory_dir = project_path / "memory"
        self.style_bible_path = self.memory_dir / "style_bible.json"
        self.gemini = GeminiClient()
        
    def _clean_json_response(self, text: str) -> dict:
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        return json.loads(cleaned.strip())
        
    def run(self):
        logger.info("Executing Stage 05: Style Bible Generation")
        
        chunk_files = sorted(list(self.chunks_dir.glob("chunk_*.txt")))
        if not chunk_files:
            raise FileNotFoundError("No chunks found. Run Stage 02 first.")
            
        # The art direction is usually established early in the novel.
        # Processing just the first chunk saves context tokens and ensures global consistency.
        with open(chunk_files[0], "r", encoding="utf-8") as f:
            chunk_text = f.read()
            
        prompt = (
            "You are an expert Art Director for a high-end Korean Manhwa adaptation.\n"
            "Based on the tone of this initial text, define the overarching visual style for the entire series.\n"
            "Return a JSON dictionary containing:\n"
            "- 'color_palette': Description of colors (e.g., 'Muted and grim' vs 'Vibrant and saturated')\n"
            "- 'lighting': General lighting aesthetic\n"
            "- 'line_art': Line style (e.g., 'Thick cinematic inks', 'Clean webtoon digital lines')\n"
            "- 'overall_mood': 1-2 sentences summarizing the visual atmosphere."
        )
        
        result_text = self.gemini.generate_json(prompt, chunk_text)
        try:
            style_data = self._clean_json_response(result_text)
            with open(self.style_bible_path, "w", encoding="utf-8") as f:
                json.dump(style_data, f, indent=2)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini output: {e}")
            raise
            
        logger.info(f"Stage 05 Complete. Style Bible established.")
