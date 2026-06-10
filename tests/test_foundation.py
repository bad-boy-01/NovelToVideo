import unittest
import tempfile
from app.models.schemas import (
    ProjectInfo, ProjectManifest, CharacterRegistryEntry, 
    CharacterVersion, CharacterFingerprint, SceneStatus, VerificationScores, Scene
)
from app.storage.project_manager import ProjectManager
from pathlib import Path

class TestFoundation(unittest.TestCase):
    def test_project_info_schema(self):
        info = ProjectInfo(
            novel_name="Test Novel",
            part=2,
            created="2026-06-10",
            chapters=10,
            chunks=5,
            scenes=100
        )
        self.assertEqual(info.novel_name, "Test Novel")
        self.assertEqual(info.part, 2)
        self.assertEqual(info.images_generated, 0) # Default value

    def test_project_manifest_schema(self):
        manifest = ProjectManifest(
            project="Test Novel",
            gemini_requests=5,
            estimated_tokens=15000
        )
        self.assertEqual(manifest.gemini_requests, 5)
        self.assertEqual(manifest.estimated_tokens, 15000)

    def test_character_fingerprint_schema(self):
        char = CharacterRegistryEntry(
            id="char_0001",
            canonical_name="Xu Changshou",
            aliases=["Little Brother"],
            fingerprint=CharacterFingerprint(
                hair="short straight black hair",
                eyes="large black eyes",
                face="round innocent face",
                skin="fair skin",
                body="small slim child",
                clothing="light brown patched robe"
            ),
            versions=[
                CharacterVersion(version=1, chapter_start=1, chapter_end=120, age="6", clothes="peasant robe"),
                CharacterVersion(version=2, chapter_start=121, chapter_end=300, age="16", clothes="sect uniform")
            ]
        )
        self.assertEqual(len(char.versions), 2)
        self.assertEqual(char.fingerprint.eyes, "large black eyes")
        self.assertEqual(char.id, "char_0001")
        
    def test_scene_schema(self):
        scene = Scene(
            scene_id=1,
            chapter="Chapter 1",
            chunk=1,
            narration="Test narration",
            tts_text="Test TTS",
            word_count=50,
            start_time=0.0,
            end_time=8.3,
            duration=8.3,
            characters=["char_0001"],
            location="marketplace",
            emotion="comedic",
            camera="wide",
            image_prompt="A marketplace",
            prompt_version="1.0",
            generator_version="0.2.1"
        )
        self.assertEqual(scene.duration, 8.3)
        self.assertEqual(scene.generator_version, "0.2.1")
        
    def test_scene_verification_scores(self):
        status = SceneStatus(
            scene_id=1,
            status="passed",
            attempts=1,
            scores=VerificationScores(
                character_consistency=9,
                scene_accuracy=8,
                composition=8,
                image_quality=9
            )
        )
        self.assertEqual(status.scores.image_quality, 9)

    def test_project_manager_folder_creation(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            pm = ProjectManager(workspace_root=tmp_path)
            project_path = pm.create_project("Rebirth of Farmer", part=1)
            
            self.assertTrue(project_path.exists())
            self.assertTrue((project_path / "failed_images").exists())
            self.assertTrue((project_path / "subtitles").exists())
            self.assertTrue((project_path / "project_info.json").exists())
            self.assertTrue((project_path / "memory/character_refs").exists())

if __name__ == '__main__':
    unittest.main()
