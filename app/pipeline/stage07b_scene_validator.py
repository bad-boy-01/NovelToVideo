import json
from pathlib import Path
from pydantic import ValidationError
from app.models.schemas import Scene
from app.utils.logger import logger

class Stage07bSceneValidator:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        
    def run(self):
        logger.info("Executing Stage 07b: Scene JSON Validator")
        
        extracted_files = sorted(list(self.scenes_dir.glob("extracted_*.json")))
        for file in extracted_files:
            with open(file, "r", encoding="utf-8") as f:
                scenes_data = json.load(f)
                
            valid_scenes = []
            for item in scenes_data:
                try:
                    scene = Scene(**item)
                    valid_scenes.append(scene)
                except ValidationError as e:
                    logger.error(f"Validation failed in {file.name}: {e}")
                    raise
            logger.info(f"{file.name}: Validated {len(valid_scenes)} scenes.")
        
        logger.info("Stage 07b Complete.")
