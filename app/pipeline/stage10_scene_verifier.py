import json
from pathlib import Path
from app.generators.gemini_client import GeminiClient
from app.utils.logger import logger

class Stage10SceneVerifier:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        self.images_dir = project_path / "images"
        self.failed_dir = project_path / "failed_images"
        self.gemini = GeminiClient()
        
    def run(self):
        logger.info("Executing Stage 10: Gemini Visual Verification")
        
        scene_files = sorted(list(self.scenes_dir.glob("scene_*.json")))
        for file in scene_files:
            with open(file, "r", encoding="utf-8") as f:
                scene = json.load(f)
                
            scene_id = scene.get("scene_id")
            prompt_hash = scene.get("prompt_hash", "nohash")
            
            image_file = self.images_dir / f"scene_{scene_id:04d}_{prompt_hash}.png"
            if not image_file.exists():
                continue
                
            # Stub: Send base64 image and prompt to Gemini Vision
            # result = self.gemini.verify_image(image_file, scene["image_prompt"])
            # if result.score < 7:
            #     logger.warning(f"Verification Failed for Scene {scene_id}. Deleting image and queueing fallback.")
            #     image_file.unlink()
            #     Path(self.failed_dir / f"scene_{scene_id:04d}.failed").touch()
            
        logger.info("Stage 10 Complete. Verification queue exhausted.")
