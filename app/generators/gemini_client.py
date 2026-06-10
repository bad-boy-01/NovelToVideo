import google.generativeai as genai
import os
import time
from app.utils.config import load_config
from app.utils.logger import logger

class GeminiClient:
    def __init__(self):
        config = load_config()
        self.model_name = config.get("gemini", {}).get("model", "gemini-2.5-flash")
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set. API calls will fail.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
    def generate_json(self, prompt: str, text: str, retries: int = 3) -> str:
        """
        Calls Gemini to generate a JSON output based on the provided prompt and text.
        Includes exponential backoff for rate limits.
        """
        full_prompt = f"{prompt}\n\n--- SOURCE TEXT ---\n{text}\n--- END SOURCE TEXT ---"
        
        for attempt in range(retries):
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.1 # Enforce highly deterministic extraction
                    )
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini API Error (Attempt {attempt+1}/{retries}): {str(e)}")
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)
