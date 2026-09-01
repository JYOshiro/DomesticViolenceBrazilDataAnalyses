import json
import math
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DATA = PROJECT_DIR / "dashboard" / "data" / "dashboard-data.json"
PREDICTION_DATA = PROJECT_DIR / "dashboard" / "data" / "prediction-data.json"
ORANGE_DIR = PROJECT_DIR / "orange"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    dashboard = json.loads(DASHBOARD_DATA.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION_DATA.read_text(encoding="utf-8"))

    for filename in (
        "daily_notification_prediction.ows",
        "prediction_train_pre_2023.tab",
        "prediction_test_2023_2025.tab",
        "README.md",
    ):
        require((ORANGE_DIR / filename).exists(), f"Missing Orange reproduction artifact: {filename}")
    require(prediction["meta"]["software"] == "Orange Data Mining 3.38.1", "Orange version is not recorded")

    annual_total = sum(row["report_count"] for row in dashboard["protectionYearly"])
    profile_dimensions = {}
    for row in dashboard["protectionProfiles"]:
        profile_dimensions.setdefault(row["dimension_name"], 0)
        profile_dimensions[row["dimension_name"]] += row["record_count"]
    for dimension in ("Suspect gender", "Victim gender", "Suspect relationship", "Violation group"):
        require(dimension in profile_dimensions, f"Missing protection profile: {dimension}")
        require(profile_dimensions[dimension] == annual_total, f"{dimension} does not reconcile to protection rows")

    yearly = {row["year"]: row["report_count"] for row in dashboard["protectionYearly"]}
    require(2020 in yearly and 2021 in yearly, "Reporting-break years are missing")
    require(yearly[2021] / yearly[2020] > 2, "Expected 2020-21 scale break is not present")

    for row in dashboard["vigitel"]:
        for field in ("weighted_current_alcohol_share", "weighted_abusive_alcohol_share"):
            value = row[field]
            require(value is None or 0 <= value <= 1, f"Invalid Vigitel percentage in {row['year']}: {field}")

    metrics = prediction["metrics"]
    for approach in ("baseline", "decisionTree", "randomForest"):
        for field in ("mae", "rmse", "r2", "recall", "precision"):
            require(math.isfinite(metrics[approach][field]), f"Prediction metric is not finite: {approach}.{field}")
    require(prediction["meta"]["trainEnd"] < prediction["meta"]["testStart"], "Prediction train/test periods overlap")
    require(
        prediction["meta"]["trainEnd"] == "2022-12-31",
        "Training period must end below 2023",
    )
    require(
        prediction["meta"]["testStart"] == "2023-01-01",
        "Test period must begin on 2023-01-01",
    )
    require(len(prediction["weekly"]) >= 156, "The 2023-forward test period is incomplete")
    require(len(prediction["meta"]["lagDefinitions"]) == 3, "Lag definitions are incomplete")
    require(
        {row["days"] for row in prediction["meta"]["lagDefinitions"]} == {1, 7, 28},
        "Lag definitions do not match the query",
    )
    for row in prediction["weekly"]:
        for field in ("actual", "decisionTree", "randomForest", "baseline"):
            require(math.isfinite(row[field]), f"Weekly prediction is not finite: {field}")
    require(len(prediction.get("examples", [])) == 3, "Prediction examples are incomplete")
    for row in prediction["examples"]:
        for field in ("actual", "decisionTree", "randomForest", "lag1", "lag7", "lag28"):
            require(math.isfinite(row[field]), f"Prediction example is not finite: {row['date']}.{field}")

    print(
        "Validated story data: all protection dimensions reconcile, the reporting break is present, "
        "Vigitel shares are bounded, and both tree models use pre-2023 training with a 2023-forward test and 1-, 7-, and 28-day lags."
    )


if __name__ == "__main__":
    main()
