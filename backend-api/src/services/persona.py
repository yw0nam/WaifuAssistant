import yaml
from pathlib import Path


def load_persona(persona_file: str = "./configs/persona.yaml") -> str:
    """페르소나 설정 로드"""
    with open(persona_file, "r", encoding="utf-8") as f:
        persona_data = yaml.safe_load(f)
    return yaml.dump(persona_data, allow_unicode=True, sort_keys=False, indent=2)
