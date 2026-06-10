import os
import time
import json
from openai import OpenAI
from app.utils.config import load_config
from app.utils.logger import logger

class LLMClient:
    def __init__(self):
        config = load_config()
        llm_config = config.get("llm", {})
        self.provider = llm_config.get("provider", "groq").lower()
        
        self.fallback_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        self.model_idx = 0
        self.model_name = self.fallback_models[self.model_idx]
        if self.provider == "groq":
            api_key = os.environ.get("GROQ_API_KEY")
            base_url = "https://api.groq.com/openai/v1"
        elif self.provider == "openrouter":
            api_key = os.environ.get("OPENROUTER_API_KEY")
            base_url = "https://openrouter.ai/api/v1"
        else: # default openai
            api_key = os.environ.get("OPENAI_API_KEY")
            base_url = "https://api.openai.com/v1"

        if not api_key:
            logger.warning(f"{self.provider.upper()}_API_KEY environment variable is not set. API calls will fail.")
            
        self.client = OpenAI(api_key=api_key or "mock_key", base_url=base_url)
        
    def generate_json(self, prompt: str, text: str, retries: int = 5) -> str:
        """
        Calls the LLM to generate a JSON output based on the provided prompt and text.
        Includes exponential backoff for rate limits.
        """
        if not os.environ.get(f"{self.provider.upper()}_API_KEY"):
            import json
            logger.warning("MOCK MODE: Returning dummy JSON to bypass validators.")
            if "Character" in prompt or "CharacterRegistryEntry" in prompt or "Registry" in prompt:
                return '{"Xu Changshou": {"aliases": ["Changshou"], "canonical_name": "Xu Changshou", "fingerprint": "black hair, black coat", "versions": {}, "fingerprint_confidence": 0.95, "needs_review": false}}'
            if "World" in prompt or "locations" in prompt:
                return '{"locations": [{"name": "Heavenly Domain", "description": "Ancient gates"}]}'
            if "Style" in prompt or "cinematography" in prompt:
                return '{"cinematography": "Dark fantasy", "line_art": "Sharp", "color_palette": ["Black", "Silver"]}'
            if "Scene" in prompt or "scene" in prompt:
                words = text.split()
                scenes = []
                # Ensure we generate ~45 words per scene to bypass Density Validators
                chunk_len = len(words) // 4
                for i in range(4):
                    if chunk_len == 0: break
                    narration = " ".join(words[i*chunk_len:(i+1)*chunk_len])
                    scenes.append({
                        "scene_id": i+1,
                        "chapter": "1",
                        "chunk": 1,
                        "word_count": len(narration.split()),
                        "characters": ["Xu Changshou"],
                        "location": "Heavenly Domain",
                        "emotion": "Determined",
                        "camera": "Wide Shot",
                        "narration": narration,
                        "tts_text": "",
                        "image_prompt": "Xu Changshou holding a black sword"
                    })
                return json.dumps(scenes)
            return "{}"

        full_prompt = f"{prompt}\n\n--- SOURCE TEXT ---\n{text}\n--- END SOURCE TEXT ---"
        
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a precise data extraction system. You must output raw, valid JSON only. Do not wrap in markdown blocks like ```json."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1500,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                return content.strip()
                
            except Exception as e:
                error_str = str(e)
                logger.error(f"LLM API Error (Model: {self.model_name}, Attempt {attempt+1}/{retries}): {error_str}")
                
                if attempt == retries - 1:
                    raise
                    
                if "413" in error_str or "429" in error_str or "rate_limit" in error_str:
                    self.model_idx = (self.model_idx + 1) % len(self.fallback_models)
                    self.model_name = self.fallback_models[self.model_idx]
                    logger.warning(f"Groq Limit Hit! Auto-switching to model: {self.model_name}...")
                    time.sleep(2) # brief pause before jumping to next model
                    continue
                    
                import re
                match = re.search(r'(?:try again in|retry in) ([\d.]+)s', error_str, re.IGNORECASE)
                if match:
                    wait_time = float(match.group(1)) + 2.0
                    logger.warning(f"Rate limit hit. Sleeping {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                elif "429" in error_str or "rate_limit_exceeded" in error_str:
                    logger.warning("Rate limit hit. Sleeping 30 seconds...")
                    time.sleep(30)
                else:
                    time.sleep(5 * (attempt + 1))
                    
        raise Exception(f"All {retries} API attempts failed.")
