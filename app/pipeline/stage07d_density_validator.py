import json
from pathlib import Path
from app.utils.logger import logger

class Stage07dDensityValidator:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        self.max_avg_words = 80
        self.max_scene_words = 120
        self.min_scene_words = 10
        
    def run(self):
        logger.info("Executing Stage 07d: Density Validator")
        
        extracted_files = sorted(list(self.scenes_dir.glob("extracted_*.json")))
        
        for file in extracted_files:
            chunk_id = file.stem.split("_")[1]
            
            with open(file, "r", encoding="utf-8") as f:
                scenes_data = json.load(f)
                
            if not scenes_data:
                continue
                
            word_counts = [len(str(s.get("narration", "")).split()) + len(str(s.get("tts_text", "")).split()) for s in scenes_data]
            
            avg_words = sum(word_counts) / len(word_counts)
            max_words = max(word_counts)
            min_words = min(word_counts)
            
            logger.info(f"Density for Chunk {chunk_id}: Avg={avg_words:.1f}, Max={max_words}, Min={min_words}")
            
            if avg_words > self.max_avg_words:
                logger.error(f"DENSITY FAILURE: Chunk {chunk_id} avg words ({avg_words:.1f}) exceeds {self.max_avg_words}. Re-extract required.")
                raise ValueError(f"Density validation failed for Chunk {chunk_id}")
                
            if max_words > self.max_scene_words:
                logger.error(f"DENSITY FAILURE: Chunk {chunk_id} has a scene with {max_words} words (Limit: {self.max_scene_words}). Re-extract required.")
                raise ValueError(f"Density validation failed for Chunk {chunk_id}")
                
        logger.info("Stage 07d Complete. All chunks passed pacing density.")
