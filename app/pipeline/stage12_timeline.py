import json
from pathlib import Path
from app.utils.logger import logger

class Stage12Timeline:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.scenes_dir = project_path / "scenes"
        self.audio_dir = project_path / "audio"
        self.images_dir = project_path / "images"
        self.timeline_file = project_path / "timeline.json"
        
    def run(self):
        logger.info("Executing Stage 12: Timeline Assembly")
        
        timeline = []
        scene_files = sorted(list(self.scenes_dir.glob("scene_*.json")))
        
        for file in scene_files:
            with open(file, "r", encoding="utf-8") as f:
                scene = json.load(f)
                
            scene_id = scene.get("scene_id")
            
            timeline.append({
                "scene": f"{scene_id:04d}",
                "audio": f"scene_{scene_id:04d}.wav",
                "duration": 6.5  # Stub: Calculates physical WAV duration
            })
            
        with open(self.timeline_file, "w", encoding="utf-8") as f:
            json.dump(timeline, f, indent=2)
            
        logger.info("Stage 12 Complete. timeline.json generated.")
