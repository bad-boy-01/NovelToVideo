import os
import json
from pathlib import Path
from datetime import datetime
from app.models.schemas import ProjectInfo

class ProjectManager:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root).resolve()
        self.projects_dir = self.root / "projects"
        
    def create_project(self, novel_name: str, part: int = 1) -> Path:
        """
        Initializes the folder structure for a given project (novel + part).
        Returns the absolute Path to the project directory.
        """
        folder_friendly_name = novel_name.lower().replace(' ', '_').replace("'", "")
        project_folder_name = f"{folder_friendly_name}_part{part}"
        project_path = self.projects_dir / project_folder_name
        
        # Core folders needed per project
        dirs_to_create = [
            "memory",
            "memory/character_refs",
            "chunks",
            "scenes",
            "images",
            "failed_images",
            "audio",
            "subtitles",
            "youtube",
            "youtube/thumbnails"
        ]
        
        for d in dirs_to_create:
            (project_path / d).mkdir(parents=True, exist_ok=True)
            
        # Initialize Project Metadata if it doesn't exist
        info_path = project_path / "project_info.json"
        if not info_path.exists():
            info = ProjectInfo(
                novel_name=novel_name,
                part=part,
                created=datetime.now().strftime("%Y-%m-%d"),
                scene_count=0,
                image_count=0,
                audio_count=0
            )
            with open(info_path, "w", encoding="utf-8") as f:
                f.write(info.model_dump_json(indent=2))
                
        return project_path

    def get_project_path(self, novel_name: str, part: int = 1) -> Path:
        folder_friendly_name = novel_name.lower().replace(' ', '_').replace("'", "")
        return self.projects_dir / f"{folder_friendly_name}_part{part}"
