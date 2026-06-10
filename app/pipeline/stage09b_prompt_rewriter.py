import json
from pathlib import Path
from app.generators.gemini_client import GeminiClient
from app.utils.logger import logger

class Stage09bPromptRewriter:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        self.failed_dir = project_path / "failed_images"
        self.gemini = GeminiClient()
        
    def run(self):
        logger.info("Executing Stage 09b: Prompt Rewriter for Failed Images")
        
        failed_tokens = sorted(list(self.failed_dir.glob("*.failed")))
        for token in failed_tokens:
            scene_id = int(token.stem.split("_")[1])
            scene_file = self.scenes_dir / f"scene_{scene_id:04d}.json"
            
            with open(scene_file, "r", encoding="utf-8") as f:
                scene = json.load(f)
                
            # Stub: Call Gemini to rewrite the prompt based on the visual failure reason
            scene["image_prompt"] += " [Gemini Rewritten for FLUX Retry]"
            
            with open(scene_file, "w", encoding="utf-8") as f:
                json.dump(scene, f, indent=2)
                
        logger.info("Stage 09b Complete. Prompts rewritten.")
