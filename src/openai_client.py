import os
import openai
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def get_openai_completion(prompt: str) -> str:
    """
    Calls the OpenAI API with the given prompt and returns the response text.
    Updated for openai>=1.0.0
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def soothing_sunset_description() -> str:
    """
    Asks GPT-3.5-turbo for a soothing description of a sunset and returns the response.
    """
    prompt = "Give me a soothing description of a sunset."
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content



    
