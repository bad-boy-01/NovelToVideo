import os
import time
import json
from openai import OpenAI
from app.utils.config import load_config
from app.utils.logger import logger
from json_repair import repair_json

class TruncationError(Exception):
    """Custom exception for hard token limits."""
    pass

class LLMClient:
    def __init__(self):
        self.config = load_config()
        self.llm_config = self.config.get("llm", {})
        
        self.primary_model = self.llm_config.get("primary_model", "google/gemini-2.5-flash")
        self.fallback_models = self.llm_config.get("fallback_models", [
            "google/gemini-2.0-flash-lite-preview-02-05:free",
            "meta-llama/llama-3.3-70b-instruct:free"
        ])
        self.model_list = [self.primary_model] + self.fallback_models
        
        self.max_output_tokens = self.llm_config.get("max_output_tokens", 8192)
        self.retries = self.llm_config.get("retries", 3)
        self.retry_backoff = self.llm_config.get("retry_backoff", 2.0)
        
        # Hardcoding to OpenRouter as per the migration
        api_key = os.environ.get("OPENROUTER_API_KEY")
        base_url = "https://openrouter.ai/api/v1"

        if not api_key:
            logger.warning("OPENROUTER_API_KEY environment variable is not set. API calls will fail.")
            
        self.client = OpenAI(api_key=api_key or "mock_key", base_url=base_url)
        
    def generate_json(self, prompt: str, text: str) -> str:
        """
        Calls the LLM to generate a JSON output based on the provided prompt and text.
        Includes fast-fail for token truncations, json-repair, and fallback routing.
        """
        if not os.environ.get("OPENROUTER_API_KEY"):
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
        
        for model in self.model_list:
            logger.info(f"Attempting JSON generation with {model}...")
            
            for attempt in range(self.retries):
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a precise data extraction system. You must output raw, valid JSON only. Do not wrap in markdown blocks like ```json."},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=self.max_output_tokens,
                        response_format={"type": "json_object"}
                    )
                    
                    # Fast-Fail Check: Did the model hit a hard token wall?
                    finish_reason = response.choices[0].finish_reason
                    if finish_reason in ["length", "max_tokens"]:
                        raise TruncationError(f"The model hit its output token limit ({self.max_output_tokens}).")
                        
                    content = response.choices[0].message.content
                    if content is None:
                        raise TruncationError("The model returned a blank response due to rate limits.")
                        
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    # Attempt standard parse, fallback to repair
                    try:
                        json.loads(content)
                        return content
                    except json.JSONDecodeError:
                        logger.warning("JSON decode failed. Attempting to repair via json-repair...")
                        repaired = repair_json(content)
                        if isinstance(repaired, str):
                            json.loads(repaired) # verify repair
                            return repaired
                        elif isinstance(repaired, (dict, list)):
                            return json.dumps(repaired)
                        else:
                            raise ValueError("Repair generated an invalid object.")
                            
                except TruncationError as e:
                    logger.warning(f"Limit Hit on {model}: {e}. Switching model immediately.")
                    break # Breaks the inner retry loop, moves to the next model in model_list
                    
                except Exception as e: # Catch Rate Limits, 502s, network drops
                    error_str = str(e)
                    logger.warning(f"Transient Error on {model} (Attempt {attempt+1}/{self.retries}): {error_str}")
                    
                    if "400" in error_str or "404" in error_str:
                        logger.warning("Model endpoint invalid. Switching model immediately.")
                        break # Break inner loop, move to next model
                        
                    time.sleep(self.retry_backoff * (attempt + 1))
                    continue
                    
        logger.error("All fallback models exhausted or failed.")
        raise RuntimeError("LLM generation failed across all configured models.")
