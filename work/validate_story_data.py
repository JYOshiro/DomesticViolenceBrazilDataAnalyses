import json
import math
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DATA = PROJECT_DIR / "dashboard" / "data" / "dashboard-data.json"
PREDICTION_DATA = PROJECT_DIR / "dashboard" / "data" / "prediction-data.json"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    dashboard = json.loads(DASHBOARD_DATA.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION_DATA.read_text(encoding="utf-8"))

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
    for field in ("mae", "rmse", "r2", "baselineMae", "recall", "precision"):
        require(math.isfinite(metrics[field]), f"Prediction metric is not finite: {field}")
    require(prediction["meta"]["trainEnd"] < prediction["meta"]["testStart"], "Prediction train/test periods overlap")
    require(len(prediction["weekly"]) >= 52, "Prediction holdout is incomplete")
    require(metrics["mae"] < metrics["baselineMae"], "Model does not improve on the stated baseline")

    print(
        "Validated story data: all protection dimensions reconcile, the reporting break is present, "
        "Vigitel shares are bounded, and prediction results use a non-overlapping 2025 holdout."
    )


if __name__ == "__main__":
    main()
