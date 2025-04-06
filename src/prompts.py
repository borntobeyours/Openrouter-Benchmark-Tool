
import json

def load_prompts(language: str = "id"):
    filepath = f"prompts/{language}_prompts.json"
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def is_valid_category(category: str, prompts: dict) -> bool:
    return category in prompts
