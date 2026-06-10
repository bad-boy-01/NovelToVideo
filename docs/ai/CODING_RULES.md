# Coding Rules

## 1. Environment Constraints
- **Kaggle Priority**: Code must be able to run sequentially in a Kaggle Jupyter notebook. Do not rely on interactive shell prompts (`input()`).
- **Dependencies**: Keep external dependencies minimal.

## 2. LLM Integrations
- **JSON Loads Protection**: *Strict Rule.* All stages that parse LLM output must NOT blindly execute `json.loads()`. The `LLMClient` must internally validate the JSON. If it encounters a `JSONDecodeError`, it must raise a specific internal exception to trigger an automatic retry on a fallback model to recover from Token Truncation scenarios.
- **Provider**: Assume `openrouter/free` meta-endpoint behavior.

## 3. General Python Standards
- **Version**: Python 3.11+
- **Typing**: Use standard Python type hints across all functions.
- **Pathing**: Use `pathlib.Path` exclusively. No string concatenations for file paths.
- **Modularity**: Stages must remain perfectly isolated classes that only communicate by reading/writing to the project directory.
