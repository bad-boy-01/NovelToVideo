import unittest
import tempfile
import json
from pathlib import Path
from app.pipeline.stage07c_coverage_validator import Stage07cCoverageValidator
from app.storage.project_manager import ProjectManager

class TestCoverageValidator(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pm = ProjectManager(workspace_root=self.tmp_dir.name)
        self.project_path = self.pm.create_project("Rebirth", part=1)
        
        self.chunks_dir = self.project_path / "chunks"
        self.scenes_dir = self.project_path / "scenes"
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock chunk with exactly 100 words
        self.chunk_text = "word " * 100
        with open(self.chunks_dir / "chunk_0001.txt", "w", encoding="utf-8") as f:
            f.write(self.chunk_text)
            
    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_coverage_success(self):
        # Create an extracted scene with 98 words (98% coverage)
        scenes = [
            {
                "narration": "word " * 49,
                "tts_text": "word " * 49
            }
        ]
        with open(self.scenes_dir / "extracted_0001.json", "w", encoding="utf-8") as f:
            json.dump(scenes, f)
            
        validator = Stage07cCoverageValidator(self.project_path)
        
        # If coverage is >= 95%, the run() method should complete without raising any exceptions.
        try:
            validator.run()
        except ValueError:
            self.fail("Validator incorrectly raised ValueError on 98% coverage.")
        
    def test_coverage_failure(self):
        # Create an extracted scene with only 80 words (80% coverage)
        # Simulating a scenario where Gemini silently skips 20% of the novel.
        scenes = [
            {
                "narration": "word " * 40,
                "tts_text": "word " * 40
            }
        ]
        with open(self.scenes_dir / "extracted_0001.json", "w", encoding="utf-8") as f:
            json.dump(scenes, f)
            
        validator = Stage07cCoverageValidator(self.project_path)
        
        # Validator should catch the data loss and deliberately crash the process.
        with self.assertRaises(ValueError):
            validator.run()

if __name__ == '__main__':
    unittest.main()
