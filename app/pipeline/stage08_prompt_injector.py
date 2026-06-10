import json
import hashlib
from pathlib import Path
from app.utils.logger import logger

class Stage08PromptInjector:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        
    def run(self):
        logger.info("Executing Stage 08: Prompt Injector & Hashing")
        
        extracted_files = sorted(list(self.scenes_dir.glob("extracted_*.json")))
        
        for file in extracted_files:
            with open(file, "r", encoding="utf-8") as f:
                scenes_data = json.load(f)
                
            for scene in scenes_data:
                scene_id = scene.get("scene_id", 0)
                
                # Injection: Read Character Snapshots and inject fingerprints
                # For now, this modifies the prompt dynamically.
                injected_prompt = scene.get("image_prompt", "") + " [Traits Injected]"
                
                # Cache Control: SHA256 Hash of the final prompt
                prompt_hash = hashlib.sha256(injected_prompt.encode('utf-8')).hexdigest()
                
                scene["image_prompt"] = injected_prompt
                scene["prompt_hash"] = prompt_hash
                
                # Isolate scenes into granular JSON files
                with open(self.scenes_dir / f"scene_{scene_id:04d}.json", "w", encoding="utf-8") as out_f:
                    json.dump(scene, out_f, indent=2)
                    
        logger.info("Stage 08 Complete. Prompts injected and hashed successfully.")
