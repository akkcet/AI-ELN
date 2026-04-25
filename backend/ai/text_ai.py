
import openai
from config import OPENAI_API_KEY, AI_MODEL

openai.api_key = OPENAI_API_KEY

# Summarize text
def summarize_text(text: str) -> str:
    resp = openai.ChatCompletion.create(
        model=AI_MODEL,
        messages=[{"role": "user", "content": f"Summarize this concisely: {text}"}]
    )
    return resp['choices'][0]['message']['content']

# Rewrite cleanly
def rewrite_text(text: str) -> str:
    resp = openai.ChatCompletion.create(
        model=AI_MODEL,
        messages=[{"role": "user", "content": f"Rewrite this professionally: {text}"}]
    )
    return resp['choices'][0]['message']['content']

# Suggest next experimental steps
def suggest_next_steps(text: str) -> str:
    resp = openai.ChatCompletion.create(
        model=AI_MODEL,
        messages=[{"role": "user", "content": f"Suggest next experimental steps for: {text}"}]
    )
    return resp['choices'][0]['message']['content']
