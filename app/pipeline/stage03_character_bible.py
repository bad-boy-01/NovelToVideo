import json
import re
from pathlib import Path
from json_repair import repair_json
from app.generators.llm_client import LLMClient
from app.utils.logger import logger

class Stage03CharacterBible:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.chunks_dir = project_path / "chunks"
        self.memory_dir = project_path / "memory"
        self.registry_path = self.memory_dir / "character_registry.json"
        self.llm = LLMClient()
        self.prompt_template_path = Path("prompts/bible_prompt.txt")
        
    def _clean_json_response(self, text: str):
        """Strips markdown formatting and attempts repair if JSON is malformed."""
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*', '', cleaned)
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            return repair_json(cleaned.strip(), return_dict=False) or {}
        
    def run(self):
        logger.info("Executing Stage 03: Character Registry Generation")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.prompt_template_path.exists():
            raise FileNotFoundError("Missing bible_prompt.txt")
            
        with open(self.prompt_template_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()
            
        chunk_files = sorted(list(self.chunks_dir.glob("chunk_*.txt")))
        if not chunk_files:
            raise FileNotFoundError("No chunks found. Run Stage 02 first.")
            
        current_registry = {}
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                current_registry = json.load(f)
                
        for chunk_file in chunk_files:
            logger.info(f"Processing {chunk_file.name} for Character updates...")
            with open(chunk_file, "r", encoding="utf-8") as f:
                chunk_text = f.read()
                
            # PASS 1: Extract Names
            logger.info(f"Pass 1: Extracting character names from {chunk_file.name}...")
            pass1_prompt = (
                "TASK:\n"
                "List ONLY character names introduced or actively appearing in this chunk.\n"
                "Rules:\n"
                "- Return a JSON array of strings (e.g. [\"Name A\", \"Name B\"])\n"
                "- No explanations. Max 10 names.\n"
            )
            
            p1_result = self.llm.generate_json(pass1_prompt, chunk_text)
            try:
                names_list = self._clean_json_response(p1_result)
                if not isinstance(names_list, list):
                    names_list = list(names_list.values()) if isinstance(names_list, dict) else []
            except Exception as e:
                logger.error(f"Failed to parse Pass 1 output for {chunk_file.name}: {e}")
                continue
                
            # Deduplicate and limit
            names_list = list(set([str(n) for n in names_list if n]))[:10]
            logger.info(f"Found {len(names_list)} characters: {names_list}")
            
            # PASS 2: Enrich Each Character
            for char_name in names_list:
                # Cache skip logic: If already in registry, we skip enrichment to save API calls
                if char_name in current_registry:
                    logger.info(f"Skipping known character: {char_name}")
                    continue
                    
                logger.info(f"Pass 2: Enriching new character: {char_name}")
                pass2_prompt = (
                    base_prompt + "\n\n"
                    f"TASK: Create a CharacterRegistryEntry ONLY for the character: {char_name}\n"
                    "Rules:\n"
                    "- ONLY base this on details found in the provided chunk.\n"
                    "- Return strict JSON matching the CharacterRegistryEntry schema.\n"
                    "- Do not include any other characters.\n"
                    "- Ensure the output is under 1200 tokens.\n"
                )
                
                p2_result = self.llm.generate_json(pass2_prompt, chunk_text)
                try:
                    entry = self._clean_json_response(p2_result)
                    
                    # Unwrap if LLM nested it under the character's name
                    if isinstance(entry, dict) and char_name in entry:
                        entry = entry[char_name]
                    elif isinstance(entry, dict) and len(entry) == 1 and isinstance(list(entry.values())[0], dict):
                        entry = list(entry.values())[0]
                        
                    # PASS 3: Local Merge
                    current_registry[char_name] = entry
                    
                    # Iteratively save progress
                    with open(self.registry_path, "w", encoding="utf-8") as f:
                        json.dump(current_registry, f, indent=2)
                        
                except Exception as e:
                    logger.error(f"Failed to parse Pass 2 output for {char_name}: {e}")
                
        logger.info(f"Stage 03 Complete. Registry secured with {len(current_registry)} characters.")
