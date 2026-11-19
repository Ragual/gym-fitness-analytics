
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = PROJECT_ROOT / "models" / "churn_model.joblib"


def load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            "Churn model not found. Train the model first."
        )

    return joblib.load(MODEL_FILE)


def predict_churn(member_data: dict) -> dict:
    saved_model = load_model()

    model = saved_model["model"]
    features = saved_model["features"]

    input_df = pd.DataFrame([member_data])

    missing_features = [
        feature for feature in features
        if feature not in input_df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    input_df = input_df[features]

    probability = float(model.predict_proba(input_df)[0][1])

    threshold = float(
        saved_model.get("threshold", 0.5)
    )

    prediction = int(probability >= threshold)

    if probability >= 0.70:
        risk_level = "HIGH"
    elif probability >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "churn_prediction": prediction,
        "churn_probability": round(probability, 4),
        "risk_level": risk_level,
        "model_name": saved_model["model_name"],
        "decision_threshold": round(threshold, 4),
    }


if __name__ == "__main__":
    sample_member = {
        "attendance_count": 5,
        "active_days": 4,
        "recent_attendance": 0,
        "failed_payments": 1,
        "payment_count": 2,
        "goals_created": 1,
        "goals_completed": 0,
        "workout_sessions": 5,
        "days_since_last_visit": 25,
        "membership_tenure_days": 180,
        "attendance_frequency": 0.06,
        "attendance_recent_ratio": 0.0,
        "goal_completion_rate": 0.0,
    }

    result = predict_churn(sample_member)

    print("\n========== CHURN PREDICTION ==========")

    for key, value in result.items():
        print(f"{key}: {value}")
