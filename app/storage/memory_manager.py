import os
import shutil
from pathlib import Path

class MemoryManager:
    def __init__(self, workspace_root: str, novel_name: str, project_path: Path):
        # Format the novel name consistently
        folder_friendly_name = novel_name.lower().replace(' ', '_').replace("'", "")
        self.global_memory_dir = Path(workspace_root).resolve() / "global_memory" / folder_friendly_name
        self.local_memory_dir = Path(project_path).resolve() / "memory"
        
    def sync_from_global(self):
        """
        Copies existing global memory to the local project, 
        ensuring absolute consistency across future novel parts.
        """
        if not self.global_memory_dir.exists():
            return # No global memory exists yet (e.g., this is Part 1)
            
        shutil.copytree(self.global_memory_dir, self.local_memory_dir, dirs_exist_ok=True)
        
    def sync_to_global(self):
        """
        Locks in the local memory updates (e.g., new characters or updated bibles)
        by copying them to the global memory folder for future parts to inherit.
        """
        if not self.local_memory_dir.exists():
            return
            
        self.global_memory_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.local_memory_dir, self.global_memory_dir, dirs_exist_ok=True)
