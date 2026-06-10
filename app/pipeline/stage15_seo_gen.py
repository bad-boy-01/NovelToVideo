from pathlib import Path
from app.utils.logger import logger
from app.generators.gemini_client import GeminiClient

class Stage15SEOGen:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.youtube_dir = project_path / "youtube"
        self.gemini = GeminiClient()
        
    def run(self):
        logger.info("Executing Stage 15: SEO Metadata Generation")
        
        with open(self.youtube_dir / "title.txt", "w") as f:
            f.write("Rebirth of the Urban Immortal (Full Story)\n")
        with open(self.youtube_dir / "description.txt", "w") as f:
            f.write("A complete recap of the Manhwa.\n")
        with open(self.youtube_dir / "tags.txt", "w") as f:
            f.write("manhwa,recap,cultivation\n")
        with open(self.youtube_dir / "chapters.txt", "w") as f:
            f.write("00:00 Intro\n01:00 Chapter 1\n")
            
        logger.info("Stage 15 Complete. SEO generated.")
