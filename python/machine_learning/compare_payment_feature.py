
import pandas as pd

from python.machine_learning.train_churn_model import (
    DATA_FILE,
    FEATURES,
    TARGET,
    TRAIN_SNAPSHOTS,
    VALIDATION_SNAPSHOT,
    TEST_SNAPSHOT,
    create_models,
    calculate_metrics,
)


def run_experiment(name, selected_features):
    df = pd.read_csv(DATA_FILE)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])

    train_dates = pd.to_datetime(TRAIN_SNAPSHOTS)
    validation_date = pd.Timestamp(VALIDATION_SNAPSHOT)
    test_date = pd.Timestamp(TEST_SNAPSHOT)

    train_df = df[df["snapshot_date"].isin(train_dates)]
    validation_df = df[df["snapshot_date"] == validation_date]
    test_df = df[df["snapshot_date"] == test_date]

    development_df = df[
        df["snapshot_date"].isin(
            train_dates.tolist() + [validation_date]
        )
    ]

    X_train = train_df[selected_features]
    y_train = train_df[TARGET]

    X_validation = validation_df[selected_features]
    y_validation = validation_df[TARGET]

    X_development = development_df[selected_features]
    y_development = development_df[TARGET]

    X_test = test_df[selected_features]
    y_test = test_df[TARGET]

    models = create_models()
    best_name = None
    best_score = -1

    for model_name, model in models.items():
        model.fit(X_train, y_train)

        metrics = calculate_metrics(
            model,
            X_validation,
            y_validation,
        )

        if metrics["roc_auc"] > best_score:
            best_score = metrics["roc_auc"]
            best_name = model_name

    final_model = create_models()[best_name]
    final_model.fit(X_development, y_development)

    test_metrics = calculate_metrics(
        final_model,
        X_test,
        y_test,
    )

    return {
        "experiment": name,
        "selected_model": best_name,
        "feature_count": len(selected_features),
        "accuracy": test_metrics["accuracy"],
        "precision": test_metrics["precision"],
        "recall": test_metrics["recall"],
        "f1_score": test_metrics["f1_score"],
        "roc_auc": test_metrics["roc_auc"],
    }


def main():
    without_payment = [
        feature for feature in FEATURES
        if feature != "payment_count"
    ]

    results = [
        run_experiment("All features", FEATURES),
        run_experiment("Without payment_count", without_payment),
    ]

    comparison = pd.DataFrame(results)

    print("\n========== PAYMENT FEATURE COMPARISON ==========")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
