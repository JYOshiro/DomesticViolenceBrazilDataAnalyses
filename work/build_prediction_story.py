import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from Orange.data import ContinuousVariable, Domain, StringVariable, Table
from Orange.regression import RandomForestRegressionLearner, TreeLearner
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


WORK_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORK_DIR.parent
COURSE_DIR = WORK_DIR.parents[2]
SOURCE = COURSE_DIR / "DayPrediction_Filtered_Holidays_daily_model_202608311605.csv"
JSON_OUTPUT = PROJECT_DIR / "dashboard" / "data" / "prediction-data.json"
SCRIPT_OUTPUT = PROJECT_DIR / "dashboard" / "data" / "prediction-data.js"
ORANGE_DIR = PROJECT_DIR / "orange"
ORANGE_TRAIN = ORANGE_DIR / "prediction_train_pre_2023.tab"
ORANGE_TEST = ORANGE_DIR / "prediction_test_2023_2025.tab"

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


def regression_metrics(actual, predicted):
    return {
        "mae": safe_number(mean_absolute_error(actual, predicted)),
        "rmse": safe_number(mean_squared_error(actual, predicted) ** 0.5),
        "r2": safe_number(r2_score(actual, predicted)),
        **classification_metrics(actual, predicted),
    }


def orange_table(frame):
    attributes = [ContinuousVariable(feature) for feature in FEATURES]
    target = ContinuousVariable("daily_dv_report_count")
    metas = [StringVariable("report_date"), ContinuousVariable("alcohol_related_report_count")]
    domain = Domain(attributes, target, metas)
    meta_values = np.empty((len(frame), 2), dtype=object)
    meta_values[:, 0] = frame["report_date"].dt.strftime("%Y-%m-%d")
    meta_values[:, 1] = frame["alcohol_related_report_count"].astype(float)
    return Table.from_numpy(
        domain,
        frame[FEATURES].to_numpy(dtype=float),
        frame["daily_dv_report_count"].to_numpy(dtype=float),
        meta_values,
    )


def permutation_importance(model, table, actual, repeats=5, seed=42):
    baseline_mae = mean_absolute_error(actual, model(table))
    rng = np.random.default_rng(seed)
    increases = []
    for feature_index, feature in enumerate(FEATURES):
        repeated = []
        for _ in range(repeats):
            permuted_x = table.X.copy()
            permuted_x[:, feature_index] = rng.permutation(permuted_x[:, feature_index])
            permuted_table = Table.from_numpy(table.domain, permuted_x, table.Y, table.metas)
            repeated.append(mean_absolute_error(actual, model(permuted_table)) - baseline_mae)
        increases.append(max(float(np.mean(repeated)), 0.0))
    total = sum(increases) or 1.0
    return sorted(
        [
            {
                "feature": feature,
                "label": FEATURE_LABELS[feature],
                "importance": safe_number(increase / total),
                "maeIncrease": safe_number(increase),
            }
            for feature, increase in zip(FEATURES, increases)
        ],
        key=lambda row: row["importance"],
        reverse=True,
    )


def main():
    frame = pd.read_csv(SOURCE, parse_dates=["report_date"])
    frame = frame.sort_values("report_date").dropna(subset=FEATURES + ["daily_dv_report_count"])
    train = frame[frame["report_date"] < "2023-01-01"].copy()
    test = frame[frame["report_date"] >= "2023-01-01"].copy()
    if train.empty or test.empty:
        raise RuntimeError("The reviewed daily source does not contain the expected pre-2023 training and 2023-forward test periods.")

    ORANGE_DIR.mkdir(parents=True, exist_ok=True)
    train_table = orange_table(train)
    test_table = orange_table(test)
    train_table.save(str(ORANGE_TRAIN))
    test_table.save(str(ORANGE_TEST))

    decision_tree = TreeLearner(
        binarize=True,
        max_depth=8,
        min_samples_leaf=10,
        min_samples_split=20,
    )
    random_forest = RandomForestRegressionLearner(
        n_estimators=500,
        max_features=8,
        min_samples_split=5,
        random_state=0,
    )
    tree_model = decision_tree(train_table)
    forest_model = random_forest(train_table)
    tree_predictions = tree_model(test_table)
    forest_predictions = forest_model(test_table)
    actual = test["daily_dv_report_count"].to_numpy()
    baseline = test["dv_reports_previous_week"].to_numpy()

    scored = test[["report_date", "daily_dv_report_count"]].copy()
    scored["decision_tree"] = tree_predictions
    scored["random_forest"] = forest_predictions
    scored["baseline"] = baseline
    scored["week"] = scored["report_date"].dt.to_period("W-SUN").dt.start_time
    weekly = (
        scored.groupby("week", as_index=False)
        .agg(
            actual=("daily_dv_report_count", "sum"),
            decision_tree=("decision_tree", "sum"),
            random_forest=("random_forest", "sum"),
            baseline=("baseline", "sum"),
        )
    )

    tree_metrics = regression_metrics(actual, tree_predictions)
    forest_metrics = regression_metrics(actual, forest_predictions)
    baseline_metrics = regression_metrics(actual, baseline)

    example_contexts = {
        "2023-03-15": "Ordinary weekday",
        "2024-07-07": "Non-holiday weekend",
        "2025-12-25": "National holiday",
    }
    examples = []
    for date, context in example_contexts.items():
        positions = np.flatnonzero(test["report_date"].to_numpy() == np.datetime64(date))
        if not len(positions):
            continue
        position = int(positions[0])
        row = test.iloc[position]
        examples.append(
            {
                "date": date,
                "context": context,
                "actual": safe_number(row["daily_dv_report_count"]),
                "decisionTree": safe_number(tree_predictions[position]),
                "randomForest": safe_number(forest_predictions[position]),
                "lag1": safe_number(row["dv_reports_previous_day"]),
                "lag7": safe_number(row["dv_reports_previous_week"]),
                "lag28": safe_number(row["dv_reports_previous_4_weeks"]),
            }
        )

    payload = {
        "meta": {
            "sourceFile": SOURCE.name,
            "outcome": "Daily domestic/family SINAN health-service notifications",
            "models": [
                "Orange Tree regression (binary tree; maximum depth 8; minimum 10 instances per leaf; do not split subsets smaller than 20)",
                "Orange Random Forest regression (500 trees; 8 attributes considered per split; replicable training; unlimited depth; do not split subsets smaller than 5)",
            ],
            "software": "Orange Data Mining 3.38.1",
            "orangeTrainFile": ORANGE_TRAIN.name,
            "orangeTestFile": ORANGE_TEST.name,
            "forecastHorizon": "One day ahead using calendar fields and notification volumes available through the prior day",
            "trainStart": train["report_date"].min().date().isoformat(),
            "trainEnd": train["report_date"].max().date().isoformat(),
            "testStart": test["report_date"].min().date().isoformat(),
            "testEnd": test["report_date"].max().date().isoformat(),
            "highVolumeDefinition": "Top 20% of days within the chronological 2023-2025 test period, evaluated by rank",
            "targetDefinition": "Daily SINAN health-service notifications dated by DT_NOTIFIC, restricted to non-self-inflicted cases (LES_AUTOP = 2) with at least one listed family, intimate-partner, former-partner, dating, sibling, child, or caregiver relationship flag.",
            "lagDefinitions": [
                {
                    "days": 1,
                    "label": "Previous day",
                    "meaning": "Yesterday's notification count; captures immediate persistence or short-lived reporting pressure.",
                },
                {
                    "days": 7,
                    "label": "Same weekday last week",
                    "meaning": "The count exactly seven calendar days earlier; preserves weekday and captures the weekly reporting rhythm.",
                },
                {
                    "days": 28,
                    "label": "Same weekday four weeks earlier",
                    "meaning": "The count exactly 28 calendar days earlier; preserves weekday while providing a steadier monthly-scale reference.",
                },
            ],
            "lagMethod": "The query first creates a complete daily calendar and fills dates without matching notifications with zero. LAG therefore means exact calendar offsets, not the previous non-empty row. The first 28 dates are excluded because at least one lag is unavailable.",
            "leakageControl": "All lag predictors refer only to earlier dates. The same-day alcohol-related count is retained as metadata and is excluded from model inputs because it would not be known before the target day is complete and is part of the same notification total.",
            "featureImportanceMethod": "Permutation importance on the 2023-2025 test data: five fixed-seed shuffles per feature, ranked by the increase in MAE and normalized for display.",
            "limitations": [
                "This predicts recorded SINAN notification volume, not the occurrence of violence.",
                "The test period is chronological; dates from 2023 onward were not used to fit either model.",
                "Dates with no matching notifications are treated as zero by the query; a true zero cannot be distinguished from an upstream coverage gap without source-system validation.",
                "Feature importance describes this model's predictive use of a variable and is not causal evidence.",
                "Reporting-system and service-use changes can reduce performance when future conditions differ from the training period.",
            ],
        },
        "metrics": {
            "meanActual": safe_number(actual.mean()),
            "baseline": baseline_metrics,
            "decisionTree": {
                **tree_metrics,
                "maeImprovementPct": safe_number(
                    (baseline_metrics["mae"] - tree_metrics["mae"]) / baseline_metrics["mae"]
                ),
            },
            "randomForest": {
                **forest_metrics,
                "maeImprovementPct": safe_number(
                    (baseline_metrics["mae"] - forest_metrics["mae"]) / baseline_metrics["mae"]
                ),
            },
        },
        "weekly": [
            {
                "week": row.week.date().isoformat(),
                "actual": safe_number(row.actual),
                "decisionTree": safe_number(row.decision_tree),
                "randomForest": safe_number(row.random_forest),
                "baseline": safe_number(row.baseline),
            }
            for row in weekly.itertuples(index=False)
        ],
        "examples": examples,
        "featureImportance": {
            "decisionTree": permutation_importance(tree_model, test_table, actual),
            "randomForest": permutation_importance(forest_model, test_table, actual),
        },
    }

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    JSON_OUTPUT.write_text(serialized, encoding="utf-8")
    SCRIPT_OUTPUT.write_text(f"window.PREDICTION_DATA = {serialized};\n", encoding="utf-8")
    print(
        f"2023-2025 test: tree MAE={tree_metrics['mae']:.1f}, "
        f"forest MAE={forest_metrics['mae']:.1f}, baseline MAE={baseline_metrics['mae']:.1f}; "
        f"tree R2={tree_metrics['r2']:.3f}, forest R2={forest_metrics['r2']:.3f}"
    )


if __name__ == "__main__":
    main()
