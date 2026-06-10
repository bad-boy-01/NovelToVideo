import shutil
from pathlib import Path
from app.utils.logger import logger

class Stage17GlobalMemory:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.memory_dir = project_path / "memory"
        self.global_dir = Path("global_memory") / self.project_path.name
        
    def run(self):
        logger.info("Executing Stage 17: Pushing to Global Memory")
        
        self.global_dir.mkdir(parents=True, exist_ok=True)
        
        if self.memory_dir.exists():
            shutil.copytree(self.memory_dir, self.global_dir, dirs_exist_ok=True)
            
        logger.info("Stage 17 Complete. Context securely locked for future chunks and parts.")
