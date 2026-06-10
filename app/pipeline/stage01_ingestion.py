import os
from pathlib import Path
from app.utils.logger import logger

class Stage01Ingestion:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.script_path = project_path / "script.txt"
        
    def run(self) -> str:
        logger.info(f"Running Stage 01: Ingestion for {self.project_path.name}")
        if not self.script_path.exists():
            raise FileNotFoundError(f"Missing script.txt at {self.script_path}")
            
        with open(self.script_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            
        # Clean up text for the chunker (standardize newlines)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # We rewrite the cleaned text back to disk for safety
        with open(self.script_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        return text
