import json
from pathlib import Path
from app.utils.logger import logger
from app.utils.config import load_config
import time

class Stage09ImageGen:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        self.images_dir = project_path / "images"
        self.failed_dir = project_path / "failed_images"
        self.config = load_config()
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)
        
    def _generate_sdxl(self, prompt: str, output_path: Path):
        """Executes SDXL inference. Optimized for T4 speed/cost efficiency."""
        logger.debug(f"Invoking Primary SDXL generator for: {prompt[:30]}...")
        time.sleep(0.1) # Stub for diffusers/API latency
        with open(output_path, "w") as f:
            f.write(f"SDXL Image Payload: {prompt}")
            
    def _generate_flux(self, prompt: str, output_path: Path):
        """Executes FLUX inference. Heavy fallback for complex scenes."""
        logger.warning(f"Invoking Heavy FLUX Fallback generator for: {prompt[:30]}...")
        time.sleep(0.5) # Stub
        with open(output_path, "w") as f:
            f.write(f"FLUX Image Payload: {prompt}")

    def run(self):
        logger.info("Executing Stage 09: Media Generation (Image Queue)")
        
        scene_files = sorted(list(self.scenes_dir.glob("scene_*.json")))
        for file in scene_files:
            with open(file, "r", encoding="utf-8") as f:
                scene = json.load(f)
                
            scene_id = scene.get("scene_id")
            prompt = scene.get("image_prompt")
            prompt_hash = scene.get("prompt_hash", "nohash")
            
            output_image = self.images_dir / f"scene_{scene_id:04d}_{prompt_hash}.png"
            failed_token = self.failed_dir / f"scene_{scene_id:04d}.failed"
            
            if output_image.exists():
                logger.debug(f"Skipping Scene {scene_id} - Cached image exists for this Hash.")
                continue
                
            # Phase 5 Hardware Fallback Architecture
            if failed_token.exists():
                logger.info(f"Scene {scene_id} previously failed Gemini Verification. Using FLUX fallback.")
                self._generate_flux(prompt, output_image)
                # Clear the failed token after a retry attempt
                failed_token.unlink()
            else:
                logger.info(f"Scene {scene_id}: Attempting primary SDXL generation.")
                self._generate_sdxl(prompt, output_image)
                
        logger.info("Stage 09 Complete. Image Queue exhausted.")
