import os
import json
from pathlib import Path
from typing import Optional
from app.models.schemas import ProjectManifest, SceneManifest, SceneStatus

class ManifestManager:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_manifest_path = project_path / "project_manifest.json"
        self.scene_manifest_path = project_path / "scenes" / "scene_manifest.json"
        
    def load_project_manifest(self, project_name: str) -> ProjectManifest:
        if self.project_manifest_path.exists():
            with open(self.project_manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ProjectManifest(**data)
        
        # Create default
        manifest = ProjectManifest(project=project_name)
        self.save_project_manifest(manifest)
        return manifest
        
    def save_project_manifest(self, manifest: ProjectManifest):
        with open(self.project_manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

    def load_scene_manifest(self) -> SceneManifest:
        if self.scene_manifest_path.exists():
            with open(self.scene_manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return SceneManifest(**data)
        
        manifest = SceneManifest()
        self.save_scene_manifest(manifest)
        return manifest
        
    def save_scene_manifest(self, manifest: SceneManifest):
        self.scene_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.scene_manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

    def update_scene_verification(self, scene_id: int, status: str):
        manifest = self.load_scene_manifest()
        
        # json keys are strings, but pydantic schema dictionary uses int for dict keys if defined
        # We will handle string-keys during deserialization by pydantic automatically, but just to be safe:
        if scene_id in manifest.verified_scenes:
            manifest.verified_scenes[scene_id].status = status
            manifest.verified_scenes[scene_id].attempts += 1
        else:
            manifest.verified_scenes[scene_id] = SceneStatus(scene_id=scene_id, status=status)
            
        self.save_scene_manifest(manifest)
