
import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from python.api.analytics_assistant import answer_question
from python.machine_learning.predict_churn import predict_churn


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_gym_api")

app = FastAPI(
    title="AI Gym Intelligence API",
    description="Gym analytics, churn prediction and Gemini AI.",
    version="2.0.0",
)


class MemberFeatures(BaseModel):
    attendance_count: int = Field(ge=0)
    active_days: int = Field(ge=0)
    recent_attendance: int = Field(ge=0)
    failed_payments: int = Field(ge=0)
    payment_count: int = Field(ge=0)
    goals_created: int = Field(ge=0)
    goals_completed: int = Field(ge=0)
    workout_sessions: int = Field(ge=0)
    days_since_last_visit: int = Field(ge=0)
    membership_tenure_days: int = Field(ge=0)
    attendance_frequency: float = Field(ge=0)
    attendance_recent_ratio: float = Field(ge=0, le=1)
    goal_completion_rate: float = Field(ge=0, le=1)


class AssistantQuestion(BaseModel):
    question: str = Field(min_length=2, max_length=500)


@lru_cache(maxsize=1)
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    http_options = types.HttpOptions(
        timeout=8000,
        retry_options=types.HttpRetryOptions(
            attempts=1,
            initial_delay=0.5,
            max_delay=2.0,
            exp_base=2.0,
            jitter=0.2,
        ),
    )

    return genai.Client(
        api_key=api_key,
        http_options=http_options,
    )


def generate_ai_answer(question: str, analytics: dict) -> str:
    client = get_gemini_client()

    prompt = f"""
You are the AI intelligence assistant for a gym management platform.

Use the verified analytics below to answer the user's question.

Instructions:
- Answer the exact question directly.
- For simple questions, respond in 2-4 sentences.
- Use bullet points only when they improve clarity.
- Provide detailed analysis only when explicitly requested.
- Use only statistics present in the verified analytics.
- Distinguish historical inactivity labels from actual churn predictions.
- Never claim inactivity automatically means membership cancellation.
- Clearly separate verified data from AI recommendations.
- Never invent member records, statistics, or cancellation reasons.
- Keep recommendations practical and specific.
- Explain technical terms in simple language.
- If the data cannot answer the question, say so.

VERIFIED ANALYTICS:
{analytics.get("answer", "No verified analytics available.")}

DATA SOURCE:
{analytics.get("source", "Unknown")}

USER QUESTION:
{question}
"""

    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input=prompt,
    )

    answer = interaction.output_text

    if not answer or not answer.strip():
        raise RuntimeError("Gemini returned an empty response.")

    return answer.strip()


@app.get("/")
def root():
    return {
        "message": "AI Gym Intelligence API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "gemini_model": GEMINI_MODEL,
        "ai_mode": "optional_with_analytics_fallback",
    }


@app.post("/predict/churn")
def churn_prediction(member: MemberFeatures):
    try:
        return predict_churn(member.model_dump())

    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    except Exception:
        logger.exception("Churn prediction failed.")

        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check API logs.",
        )


@app.post("/assistant/ask")
def ask_assistant(request: AssistantQuestion):
    # Step 1: Retrieve verified analytics.
    try:
        analytics = answer_question(request.question)

    except Exception:
        logger.exception("Analytics retrieval failed.")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve verified analytics.",
        )

    # Step 2: Try Gemini AI.
    try:
        ai_answer = generate_ai_answer(
            request.question,
            analytics,
        )

        logger.info("Gemini generated an AI answer.")

        return {
            "answer": ai_answer,
            "source": analytics.get("source", "analytics"),
            "mode": "gemini",
            "model": GEMINI_MODEL,
        }

    # Step 3: Use deterministic analytics if Gemini fails.
    except Exception as error:
        logger.exception(
            "Gemini generation failed: %s",
            type(error).__name__,
        )

        fallback_answer = analytics.get(
            "answer",
            "AI assistance is temporarily unavailable. Please try again later.",
        )

        logger.warning(
            "Returning deterministic analytics fallback."
        )

        return {
            "answer": fallback_answer,
            "source": analytics.get("source", "analytics"),
            "mode": "analytics_fallback",
            "fallback_reason": "Gemini temporarily unavailable",
        }
