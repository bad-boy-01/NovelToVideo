import json
from pathlib import Path
from app.utils.logger import logger

class Stage16YouTubePackage:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.youtube_dir = project_path / "youtube"
        
    def run(self):
        logger.info("Executing Stage 16: YouTube JSON Packaging")
        
        package = {
            "title": "Rebirth of the Urban Immortal (Full Story)",
            "video_file": "final_video.mp4",
            "thumbnail": "thumbnail_final.png",
            "ready_for_upload": True
        }
        
        with open(self.youtube_dir / "upload_package.json", "w") as f:
            json.dump(package, f, indent=2)
            
        logger.info("Stage 16 Complete. Output is ready for upload.")
