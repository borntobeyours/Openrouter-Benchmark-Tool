import time
import random

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        return result, round(time.time() - start, 2)
    return wrapper

import requests
import os

def evaluate_response(response_text):
    """
    Dummy evaluator that returns a random score between 1 and 10.
    Replace this with actual evaluation logic.
    """
    return random.randint(1, 10)

def evaluate_response_with_llm(response_text, api_key=None, model="openai/gpt-4"):
    """
    Use an LLM to evaluate the quality of a response and return a score from 1 to 10.
    """
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("No API key found for OpenRouter.")
        return None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Please rate the quality of the following response on a scale of 1 to 10, where 1 is very poor and 10 is excellent. Only reply with the number.\n\nResponse:\n{response_text}"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        res.raise_for_status()
        content = res.json()['choices'][0]['message']['content']
        print(f"LLM raw evaluation response: {content}")
        # Extract the first integer found in the response
        import re
        match = re.search(r'\b([1-9]|10)\b', content)
        if match:
            score = int(match.group(1))
            print(f"Extracted evaluator score: {score}")
            return score
        else:
            print("No valid score found in LLM response.")
            return None
    except Exception as e:
        print(f"LLM evaluation failed: {e}")
        return None
    return wrapper


def evaluate_metric_with_llm(response_text, metric_name, instructions, api_key=None, model="openai/gpt-4"):
    """
    Use an LLM to evaluate a specific metric of a response.
    """
    import requests, os, re
    if api_key is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("No API key found for OpenRouter.")
        return None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Please rate the following response on the metric '{metric_name}' from 1 to 10.\n"
    prompt += f"Instructions: {instructions}\n\n"
    prompt += f"Response:\n{response_text}\n\n"
    prompt += "Only reply with the number."

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        res.raise_for_status()
        content = res.json()['choices'][0]['message']['content']
        print(f"LLM {metric_name} evaluation response: {content}")
        match = re.search(r'\b([1-9]|10)\b', content)
        if match:
            score = int(match.group(1))
            print(f"Extracted {metric_name} score: {score}")
            return score
        else:
            print(f"No valid score found in LLM response for {metric_name}.")
            return None
    except Exception as e:
        print(f"LLM {metric_name} evaluation failed: {e}")
        return None


def evaluate_factual_accuracy(response_text):
    """Dummy factual accuracy score 1-10"""
    return random.randint(1, 10)

def evaluate_consistency(response_text):
    """Dummy consistency score 1-10"""
    return random.randint(1, 10)

def evaluate_robustness(response_text):
    """Dummy robustness score 1-10"""
    return random.randint(1, 10)

def evaluate_creativity(response_text):
    """Dummy creativity/diversity score 1-10"""
    return random.randint(1, 10)

def evaluate_toxicity(response_text):
    """Dummy toxicity score 1-10 (lower is better)"""
    return random.randint(1, 10)

def evaluate_relevance(response_text):
    """Dummy relevance score 1-10"""
    return random.randint(1, 10)

def evaluate_fluency(response_text):
    """Dummy fluency score 1-10"""
    return random.randint(1, 10)

def evaluate_token_efficiency(response_text):
    """Dummy token efficiency score 1-10"""
    return random.randint(1, 10)

def detect_failure(response_text):
    """Dummy failure detection: True if failed"""
    return False
