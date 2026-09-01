import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


WORK_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORK_DIR.parent
COURSE_DIR = WORK_DIR.parents[2]
SOURCE = COURSE_DIR / "DayPrediction_Filtered_Holidays_daily_model_202608311605.csv"
JSON_OUTPUT = PROJECT_DIR / "dashboard" / "data" / "prediction-data.json"
SCRIPT_OUTPUT = PROJECT_DIR / "dashboard" / "data" / "prediction-data.js"

FEATURES = [
    "day_of_week_number",
    "is_weekend",
    "month_number",
    "quarter_number",
    "days_since_start",
    "is_calendar_event",
    "is_national_holiday",
    "dv_reports_previous_day",
    "dv_reports_previous_week",
    "dv_reports_previous_4_weeks",
]

FEATURE_LABELS = {
    "day_of_week_number": "Day of week",
    "is_weekend": "Weekend",
    "month_number": "Month",
    "quarter_number": "Quarter",
    "days_since_start": "Long-term time trend",
    "is_calendar_event": "Calendar event",
    "is_national_holiday": "National holiday",
    "dv_reports_previous_day": "Previous day volume",
    "dv_reports_previous_week": "Same weekday last week",
    "dv_reports_previous_4_weeks": "Same weekday four weeks earlier",
}


def safe_number(value):
    value = float(value)
    return value if math.isfinite(value) else None


def classification_metrics(actual, predicted):
    actual_threshold = np.quantile(actual, 0.8)
    predicted_threshold = np.quantile(predicted, 0.8)
    actual_high = actual >= actual_threshold
    predicted_high = predicted >= predicted_threshold
    true_positive = int((actual_high & predicted_high).sum())
    false_positive = int((~actual_high & predicted_high).sum())
    false_negative = int((actual_high & ~predicted_high).sum())
    true_negative = int((~actual_high & ~predicted_high).sum())
    return {
        "actualThreshold": safe_number(actual_threshold),
        "predictedThreshold": safe_number(predicted_threshold),
        "precision": safe_number(true_positive / (true_positive + false_positive))
        if true_positive + false_positive
        else None,
        "recall": safe_number(true_positive / (true_positive + false_negative))
        if true_positive + false_negative
        else None,
        "accuracy": safe_number((true_positive + true_negative) / len(actual)),
        "actualHighDays": int(actual_high.sum()),
        "predictedHighDays": int(predicted_high.sum()),
    }


def main():
    frame = pd.read_csv(SOURCE, parse_dates=["report_date"])
    frame = frame.sort_values("report_date").dropna(subset=FEATURES + ["daily_dv_report_count"])
    train = frame[frame["report_date"] < "2025-01-01"].copy()
    test = frame[(frame["report_date"] >= "2025-01-01") & (frame["report_date"] < "2026-01-01")].copy()
    if train.empty or test.empty:
        raise RuntimeError("The reviewed daily source does not contain the expected training and 2025 holdout periods.")

    model = RandomForestRegressor(
        n_estimators=500,
        max_features=0.8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(train[FEATURES], train["daily_dv_report_count"])
    predictions = model.predict(test[FEATURES])
    actual = test["daily_dv_report_count"].to_numpy()
    baseline = test["dv_reports_previous_week"].to_numpy()

    mae = mean_absolute_error(actual, predictions)
    baseline_mae = mean_absolute_error(actual, baseline)
    rmse = mean_squared_error(actual, predictions) ** 0.5
    baseline_rmse = mean_squared_error(actual, baseline) ** 0.5
    scored = test[["report_date", "daily_dv_report_count"]].copy()
    scored["predicted"] = predictions
    scored["week"] = scored["report_date"].dt.to_period("W-SUN").dt.start_time
    weekly = (
        scored.groupby("week", as_index=False)
        .agg(actual=("daily_dv_report_count", "sum"), predicted=("predicted", "sum"))
    )

    payload = {
        "meta": {
            "sourceFile": SOURCE.name,
            "outcome": "Daily domestic/family SINAN health-service notifications",
            "model": "Random forest regression",
            "forecastHorizon": "One day ahead using calendar fields and notification volumes available through the prior day",
            "trainStart": train["report_date"].min().date().isoformat(),
            "trainEnd": train["report_date"].max().date().isoformat(),
            "testStart": test["report_date"].min().date().isoformat(),
            "testEnd": test["report_date"].max().date().isoformat(),
            "highVolumeDefinition": "Top 20% of days within the chronological 2025 holdout, evaluated by rank",
            "limitations": [
                "This predicts recorded SINAN notification volume, not the occurrence of violence.",
                "The holdout is chronological; 2025 was not used to fit the model.",
                "Feature importance describes this model's predictive use of a variable and is not causal evidence.",
                "Reporting-system and service-use changes can reduce performance when future conditions differ from the training period.",
            ],
        },
        "metrics": {
            "mae": safe_number(mae),
            "rmse": safe_number(rmse),
            "r2": safe_number(r2_score(actual, predictions)),
            "meanActual": safe_number(actual.mean()),
            "baselineMae": safe_number(baseline_mae),
            "baselineRmse": safe_number(baseline_rmse),
            "maeImprovementPct": safe_number((baseline_mae - mae) / baseline_mae),
            **classification_metrics(actual, predictions),
            "baselineHighVolumePrecision": classification_metrics(actual, baseline)["precision"],
            "baselineHighVolumeRecall": classification_metrics(actual, baseline)["recall"],
        },
        "weekly": [
            {
                "week": row.week.date().isoformat(),
                "actual": safe_number(row.actual),
                "predicted": safe_number(row.predicted),
            }
            for row in weekly.itertuples(index=False)
        ],
        "featureImportance": sorted(
            [
                {
                    "feature": feature,
                    "label": FEATURE_LABELS[feature],
                    "importance": safe_number(importance),
                }
                for feature, importance in zip(FEATURES, model.feature_importances_)
            ],
            key=lambda row: row["importance"],
            reverse=True,
        ),
    }

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    JSON_OUTPUT.write_text(serialized, encoding="utf-8")
    SCRIPT_OUTPUT.write_text(f"window.PREDICTION_DATA = {serialized};\n", encoding="utf-8")
    print(
        f"2025 holdout: MAE={mae:.1f}, baseline MAE={baseline_mae:.1f}, "
        f"improvement={(baseline_mae - mae) / baseline_mae:.1%}, R2={r2_score(actual, predictions):.3f}"
    )


if __name__ == "__main__":
    main()
