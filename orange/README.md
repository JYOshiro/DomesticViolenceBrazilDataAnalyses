# Reproduce the prediction in Orange

Open `daily_notification_prediction.ows` in Orange Data Mining 3.38.1 or later. The workflow uses two native Orange data files:

- `prediction_train_pre_2023.tab`: training observations from 29 January 2012 through 31 December 2022.
- `prediction_test_2023_2025.tab`: untouched test observations from 1 January 2023 through 31 December 2025.

The first 28 source dates are absent because the 28-day lag is not yet available.

## Column roles

- Target: `daily_dv_report_count`.
- Features: day-of-week number, weekend flag, month, quarter, days since start, calendar-event flag, national-holiday flag, and the 1-, 7-, and 28-day notification lags.
- Meta: `report_date` and `alcohol_related_report_count`.

The alcohol-related count is intentionally metadata. It is measured on the target day and is part of the daily total, so using it as a feature would leak same-day outcome information.

## Widget settings

### Tree

- Induce binary tree: on
- Minimum instances in leaves: 10
- Do not split subsets smaller than: 20
- Maximum tree depth: 8
- Majority stopping rule: off (classification-only setting)

### Random Forest

- Number of trees: 500
- Number of attributes considered at each split: 8
- Replicable training: on (Orange uses seed 0)
- Maximum depth: off / unlimited
- Do not split subsets smaller than: 5
- Balance class distribution: off (classification-only setting)

### Test & Score

- Training `Data`: `prediction_train_pre_2023.tab`
- `Test Data`: `prediction_test_2023_2025.tab`
- Evaluation method: **Test on test data**
- Display regression metrics: MAE, RMSE, and R²

Do not use random sampling or ordinary cross-validation across the combined dataset. That would allow later dates into training and would no longer reproduce the chronological test.

## Expected model results

The website data is generated with Orange's own learners, using the settings above:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Tree | 93.0 | 122.3 | 0.557 |
| Random Forest | 83.5 | 109.0 | 0.648 |

Small display-rounding differences are acceptable; a material difference usually means the target/metadata roles or the Test & Score evaluation method is different.

The “same weekday last week” baseline is not an Orange learner. It is calculated directly as `dv_reports_previous_week`, which equals the target from exactly seven calendar days earlier. Its MAE is 70.4, so neither Orange model improves on this benchmark under the selected chronological split.
