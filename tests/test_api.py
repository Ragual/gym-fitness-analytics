
from python.api.analytics_assistant import answer_question
from fastapi.testclient import TestClient

from python.api.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "AI Gym Intelligence API is running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_churn_prediction_endpoint():
    payload = {
        "attendance_count": 2,
        "active_days": 2,
        "recent_attendance": 0,
        "failed_payments": 1,
        "payment_count": 1,
        "goals_created": 1,
        "goals_completed": 0,
        "workout_sessions": 2,
        "days_since_last_visit": 75,
        "membership_tenure_days": 180,
        "attendance_frequency": 0.02,
        "attendance_recent_ratio": 0.0,
        "goal_completion_rate": 0.0,
    }

    response = client.post("/predict/churn", json=payload)

    assert response.status_code == 200

    result = response.json()

    assert result["churn_prediction"] in [0, 1]
    assert 0 <= result["churn_probability"] <= 1
    assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert result["model_name"] == "random_forest"
    assert 0 <= result["decision_threshold"] <= 1


def test_invalid_prediction_input():
    response = client.post(
        "/predict/churn",
        json={"attendance_count": -1},
    )

    assert response.status_code == 422


def test_assistant_total_members():
    result = answer_question("How many members are registered?")

    assert result["source"] == "member_features"
    assert "549" in result["answer"]
    assert "2,000" in result["answer"]


def test_assistant_churn_question():
    result = answer_question(
        "How many members are at risk of churn?"
    )

    assert result["source"] == "member_features"
    assert "15 out of 549" in result["answer"]
    assert "2.73%" in result["answer"]
    assert "30-day" in result["answer"]


def test_assistant_workout_recommendation():
    result = answer_question(
        "Which workout recommendation is most common?"
    )

    assert result["source"] == "workout_recommendations"
    assert "Goal-focused training: 305" in result["answer"]


def test_assistant_segmentation():
    result = answer_question(
        "How many members are in each segment?"
    )

    assert result["source"] == "member_segments"
    assert "4 groups" in result["answer"]
    assert "Segment 0: 93" in result["answer"]
    assert "Segment 1: 249" in result["answer"]


def test_assistant_goal_completion():
    result = answer_question(
        "What is the goal completion rate?"
    )

    assert result["source"] == "member_features"
    assert "624" in result["answer"]
    assert "213" in result["answer"]
    assert "34.13%" in result["answer"]


def test_assistant_empty_question():
    result = answer_question("")

    assert result["source"] == "input_validation"

def test_assistant_gemini_failure_uses_analytics_fallback(monkeypatch):
    from python.api import main

    def simulate_gemini_failure(question, analytics):
        raise TimeoutError("Simulated Gemini timeout")

    monkeypatch.setattr(
        main,
        "generate_ai_answer",
        simulate_gemini_failure,
    )

    response = client.post(
        "/assistant/ask",
        json={"question": "How many members are in the analytics cohort?"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["mode"] == "analytics_fallback"
    assert result["source"] == "member_features"
    assert "549" in result["answer"]
    assert result["fallback_reason"] == "Gemini temporarily unavailable"
