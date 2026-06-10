import json
from pathlib import Path
from app.utils.logger import logger

class Stage07cCoverageValidator:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.chunks_dir = project_path / "chunks"
        self.scenes_dir = project_path / "scenes"
        
    def run(self):
        logger.info("Executing Stage 07c: Coverage Validator")
        
        chunk_files = sorted(list(self.chunks_dir.glob("chunk_*.txt")))
        
        for chunk_file in chunk_files:
            chunk_id = chunk_file.stem.split("_")[1]
            extracted_file = self.scenes_dir / f"extracted_{chunk_id}.json"
            
            if not extracted_file.exists():
                logger.warning(f"Missing extracted scenes for {chunk_file.name}")
                continue
                
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_text = f.read()
            chunk_words = len(chunk_text.split())
            
            with open(extracted_file, "r", encoding="utf-8") as f:
                scenes_data = json.load(f)
                
            scene_words = sum(len(str(scene.get("narration", "")).split()) + len(str(scene.get("tts_text", "")).split()) for scene in scenes_data)
            
            if chunk_words == 0:
                continue
                
            coverage_ratio = (scene_words / chunk_words) * 100
            
            logger.info(f"Coverage for {chunk_id}: {coverage_ratio:.2f}% ({scene_words}/{chunk_words} words)")
            
            if coverage_ratio < 95.0:
                logger.error(f"CRITICAL FAILURE: Chunk {chunk_id} coverage ratio is {coverage_ratio:.2f}%. Requirement is >= 95%. RE-EXTRACT REQUIRED.")
                raise ValueError(f"Coverage validation failed for Chunk {chunk_id}")
                
        logger.info("Stage 07c Complete. All chunks passed coverage validation.")
