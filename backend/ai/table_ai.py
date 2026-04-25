
import pandas as pd
import openai
from config import AI_MODEL, OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# AI table insights
def analyze_table(df: pd.DataFrame) -> str:
    csv = df.to_csv(index=False)
    prompt = f"Analyze the following CSV table and summarize patterns:{csv}"

    resp = openai.ChatCompletion.create(
        model=AI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp['choices'][0]['message']['content']
