
import json

def load_prompts(filepath="prompts/default_prompts.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def is_valid_category(category: str, prompts: dict) -> bool:
    return category in prompts
