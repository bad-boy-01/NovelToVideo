import unittest
import tempfile
import json
from pathlib import Path
from app.pipeline.stage07d_density_validator import Stage07dDensityValidator
from app.storage.project_manager import ProjectManager

class TestDensityValidator(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pm = ProjectManager(workspace_root=self.tmp_dir.name)
        self.project_path = self.pm.create_project("DensityTest", part=1)
        
        self.scenes_dir = self.project_path / "scenes"
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
            
    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_density_success(self):
        # Mock 5 scenes, each containing exactly 60 words (Perfect 4-8s pacing)
        scenes = [{"narration": "word " * 30, "tts_text": "word " * 30} for _ in range(5)]
        
        with open(self.scenes_dir / "extracted_0001.json", "w", encoding="utf-8") as f:
            json.dump(scenes, f)
            
        validator = Stage07dDensityValidator(self.project_path)
        try:
            validator.run()
        except ValueError:
            self.fail("Validator incorrectly crashed on a perfect 60-word average.")

    def test_density_avg_failure(self):
        # Mock 5 scenes, each containing 90 words (Exceeds 80 average limit)
        scenes = [{"narration": "word " * 45, "tts_text": "word " * 45} for _ in range(5)]
        
        with open(self.scenes_dir / "extracted_0001.json", "w", encoding="utf-8") as f:
            json.dump(scenes, f)
            
        validator = Stage07dDensityValidator(self.project_path)
        # Should deliberately crash to force a chunk re-extraction
        with self.assertRaises(ValueError):
            validator.run()
            
    def test_density_max_failure(self):
        # Mock scenes: 4 very short ones (10 words), but 1 massive one (130 words)
        # The average is fine (~34 words), but the 130-word scene exceeds the absolute max limit of 120.
        scenes = [{"narration": "word " * 5, "tts_text": "word " * 5} for _ in range(4)]
        scenes.append({"narration": "word " * 65, "tts_text": "word " * 65})
        
        with open(self.scenes_dir / "extracted_0001.json", "w", encoding="utf-8") as f:
            json.dump(scenes, f)
            
        validator = Stage07dDensityValidator(self.project_path)
        # Should deliberately crash to prevent the 130-word scene from reaching video assembly
        with self.assertRaises(ValueError):
            validator.run()

if __name__ == '__main__':
    unittest.main()
