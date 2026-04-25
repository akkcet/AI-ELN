import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
import asyncio
load_dotenv()  # Ensures .env variables are loaded

# ✅ Azure config
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")           #  https://my-resource.openai.azure.com
AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")                 # key
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")       # deployed model name, e.g. "gpt-4o-mini"

if not AZURE_ENDPOINT or not AZURE_KEY or not AZURE_DEPLOYMENT:
    raise RuntimeError("Azure OpenAI environment variables missing!")

#  WORKING CLIENT (Python 3.13 )


def generate_experiment_from_topic(topic: str):

    prompt = f"""
    You are a scientific researcher assistant.
    Generate a structured experiment for an Electronic Lab Notebook (ELN).

    Topic: "{topic}"

    Return ONLY valid JSON with keys:
    - title
    - Aims
    - Background
    - Method
    - Observations
    - Results
    - Conclusion
    """
    client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,    # mandatory
        messages=[
            {"role": "system", "content": "You generate ELN-format experiments."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    print("RAW AI OUTPUT:", content)
    return json.loads(content)
def generate_experiment_summary(topic: str):

    prompt = f"""
    You are a scientific researcher assistant.
    Generate a detailed experiment summary for an Electronic Lab Notebook (ELN) section. Only generate a summary.Dont handle chemistry logic.

    experiment content: "{topic}"

    """
    client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,    # mandatory
        messages=[
            {"role": "system", "content": "You are a scientific researcher.Always respond **ONLY** in JSON format with a field named 'summary'."},
            {"role": "user", "content": prompt}
        ],
        temperature=1.0,response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    #print("RAW AI OUTPUT:", content)
    return json.loads(content)


def generate_experiment_review_comment(text: str):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an assistant who writes **professional review comments** "
                    "about experiment documentation. "
                    "Your output must be a single short paragraph in JSON field 'review'."
                )
            },
            {
                "role": "user",
                "content": f"Write a review comment for this experiment:\n\n{text}"
            }
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }
    client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=payload["messages"],
        temperature=payload["temperature"],
        response_format=payload["response_format"],
    )

    result = response.choices[0].message.content
    return json.loads(result)


async def answer_question_safe(question: str, context: str) -> str:
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

    AZURE_CHAT_MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT")  

    """
    Safe text-only QA function.
    Answers ONLY from given context.
    No chemistry reasoning, no predictions.
    """

    system_prompt = (
        "You are a helpful assistant that answers questions ONLY using the provided context. "
        "If the answer is not in the context, reply: "
        "'I don't know based on the provided documents.' "
        "Do NOT give scientific, lab, chemical, or experimental advice. "
        "Do NOT fill in missing information. "
        "Stay strictly grounded in the user-provided context."
    )

    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above."
    )

    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=AZURE_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

# -----------------------------------------------------
#  Small-talk model (text-only, safe)
# -----------------------------------------------------

async def smalltalk_response(message: str) -> str:
    system_prompt = (
        "You are a friendly assistant. Keep answers very short and helpful. "
        "Do NOT offer scientific, laboratory, or chemical advice. "
        "Only handle social conversation like greetings or small talk. " \
        "Do not discuss about any country or politics or conflict"\
        "Your name is ELN agent"
    )

    user_prompt = f"User said: {message}"
    client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"))
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6
    )

    return response.choices[0].message.content.strip()
