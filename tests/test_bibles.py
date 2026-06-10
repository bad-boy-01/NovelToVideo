import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch
from app.pipeline.stage03_character_bible import Stage03CharacterBible
from app.pipeline.stage04_world_bible import Stage04WorldBible
from app.pipeline.stage05_style_bible import Stage05StyleBible
from app.storage.project_manager import ProjectManager

class TestBibles(unittest.TestCase):
    def setUp(self):
        # Create a temporary project workspace
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pm = ProjectManager(workspace_root=self.tmp_dir.name)
        self.project_path = self.pm.create_project("Rebirth Test", part=1)
        
        # Create dummy text chunks needed by the Bible generators
        chunks_dir = self.project_path / "chunks"
        with open(chunks_dir / "chunk_0001.txt", "w", encoding="utf-8") as f:
            f.write("Chapter 1: The boy named Xu Changshou lived in the Heavenly Sect.")
            
        # Ensure the prompt templates exist so the stages don't crash
        self.prompts_dir = Path("prompts")
        self.prompts_dir.mkdir(exist_ok=True)
        with open(self.prompts_dir / "bible_prompt.txt", "w", encoding="utf-8") as f:
            f.write("Test Prompt")

    def tearDown(self):
        self.tmp_dir.cleanup()

    @patch('app.pipeline.stage03_character_bible.GeminiClient')
    def test_character_bible_generation(self, MockGemini):
        # Mock Gemini returns JSON
        mock_instance = MockGemini.return_value
        mock_instance.generate_json.return_value = '''
        {
            "char_0001": {
                "id": "char_0001",
                "canonical_name": "Xu Changshou",
                "aliases": ["Changshou"],
                "fingerprint": {"hair": "black"},
                "versions": []
            }
        }
        '''
        
        stage = Stage03CharacterBible(self.project_path)
        stage.run()
        
        registry_path = self.project_path / "memory" / "character_registry.json"
        self.assertTrue(registry_path.exists())
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["char_0001"]["canonical_name"], "Xu Changshou")

    @patch('app.pipeline.stage04_world_bible.GeminiClient')
    def test_world_bible_generation(self, MockGemini):
        mock_instance = MockGemini.return_value
        mock_instance.generate_json.return_value = '''
        {
            "Heavenly Sect": {
                "description": "A floating mountain sect."
            }
        }
        '''
        
        stage = Stage04WorldBible(self.project_path)
        stage.run()
        
        bible_path = self.project_path / "memory" / "world_bible.json"
        self.assertTrue(bible_path.exists())
        with open(bible_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertIn("Heavenly Sect", data)

    @patch('app.pipeline.stage05_style_bible.GeminiClient')
    def test_style_bible_generation(self, MockGemini):
        mock_instance = MockGemini.return_value
        mock_instance.generate_json.return_value = '''
        {
            "color_palette": "Muted and grim",
            "lighting": "Dark",
            "line_art": "Thick inks",
            "overall_mood": "Grimdark fantasy"
        }
        '''
        
        stage = Stage05StyleBible(self.project_path)
        stage.run()
        
        bible_path = self.project_path / "memory" / "style_bible.json"
        self.assertTrue(bible_path.exists())
        with open(bible_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["overall_mood"], "Grimdark fantasy")

if __name__ == '__main__':
    unittest.main()
