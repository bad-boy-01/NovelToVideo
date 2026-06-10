import json
import re
from pathlib import Path
from app.generators.llm_client import LLMClient
from app.utils.logger import logger

class Stage07aSceneExtractor:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.chunks_dir = project_path / "chunks"
        self.scenes_dir = project_path / "scenes"
        self.llm = LLMClient()
        
    def _clean_json_response(self, text: str) -> list:
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        return json.loads(cleaned.strip())
        
    def run(self):
        logger.info("Executing Stage 07a: Scene Extraction")
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        
        chunk_files = sorted(list(self.chunks_dir.glob("chunk_*.txt")))
        
        for chunk_file in chunk_files:
            logger.info(f"Extracting scenes for {chunk_file.name}...")
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_text = f.read()
                
            prompt = (
                "You are an expert Manhwa Scriptwriter. Convert the following novel text into a sequential array of video scenes.\n"
                "CRITICAL INSTRUCTION: Do NOT skip any dialogue or story events. The extracted text MUST cover >= 95% of the original chunk.\n"
                "Target pacing: 1 scene every 4-8 seconds.\n"
                "Return a JSON list of Scene objects. Each Scene object MUST strictly adhere to this exact schema:\n"
                "{\n"
                '  "scene_id": <int>,\n'
                '  "chapter": "<string>",\n'
                '  "chunk": <int>,\n'
                '  "narration": "<string: exact text from the novel>",\n'
                '  "tts_text": "<string: text to be spoken by TTS>",\n'
                '  "word_count": <int: number of words in narration>,\n'
                '  "characters": ["<string>"],\n'
                '  "location": "<string>",\n'
                '  "emotion": "<string>",\n'
                '  "camera": "<string>",\n'
                '  "image_prompt": "<string>"\n'
                "}\n"
            )
            
            try:
                result_text = self.llm.generate_json(prompt, chunk_text)
                scenes = self._clean_json_response(result_text)
                
                chunk_id = chunk_file.stem.split("_")[1]
                with open(self.scenes_dir / f"extracted_{chunk_id}.json", "w", encoding="utf-8") as f:
                    json.dump(scenes, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to extract scenes for {chunk_file.name}: {e}")
                raise
                
        logger.info("Stage 07a Complete.")
