import yaml
from pathlib import Path

def load_config(config_path: str = "configs/config.yaml") -> dict:
    path = Path(config_path).resolve()
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
