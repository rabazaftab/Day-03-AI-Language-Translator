import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL = "openai/gpt-4.1-mini"


class TranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    source_language: str
    target_language: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/translate")
async def translate(data: TranslationRequest):

    if not OPENROUTER_API_KEY:
        return JSONResponse(
            status_code=500,
            content={
                "error": "OpenRouter API key is not configured."
            }
        )

    prompt = f"""
You are a professional language translator.

Translate the user's text from {data.source_language}
to {data.target_language}.

Rules:
1. Preserve the original meaning.
2. Do not add explanations.
3. Do not add notes.
4. Return ONLY valid JSON.
5. The JSON must contain exactly these fields:
   translation
   source_language
   target_language

Required format:

{{
    "translation": "translated text",
    "source_language": "{data.source_language}",
    "target_language": "{data.target_language}"
}}

Text to translate:
{data.text}
"""

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "OpenRouter request failed.",
                    "details": response.text
                }
            )

        result = response.json()

        content = result["choices"][0]["message"]["content"]

        # Remove possible markdown code fences
        content = content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        translated_data = json.loads(content)

        required_fields = {
            "translation",
            "source_language",
            "target_language"
        }

        if not required_fields.issubset(translated_data.keys()):
            raise ValueError("Invalid LLM response structure.")

        return {
            "translation": translated_data["translation"],
            "source_language": translated_data["source_language"],
            "target_language": translated_data["target_language"]
        }

    except json.JSONDecodeError:

        return JSONResponse(
            status_code=500,
            content={
                "error": "The AI returned an invalid JSON response."
            }
        )

    except requests.RequestException:

        return JSONResponse(
            status_code=500,
            content={
                "error": "Unable to connect to OpenRouter."
            }
        )

    except Exception as error:

        return JSONResponse(
            status_code=500,
            content={
                "error": f"Unexpected error: {str(error)}"
            }
        )