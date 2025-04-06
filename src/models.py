
MODELS = [
    "meta-llama/llama-4-maverick:free",
    "meta-llama/llama-4-scout:free",
    "openrouter/quasar-alpha",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "anthropic/claude-3.5-sonnet",
    "deepseek/deepseek-chat-v3-0324",
    "anthropic/claude-3.7-sonnet",
    "google/gemini-2.5-pro-exp-03-25:free",
    "openai/gpt-4o-mini"
]

def is_valid_model(model: str) -> bool:
    return model in MODELS
