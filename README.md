# Alcohol and Reporting Context Dashboard

Static capstone dashboard built from aggregated SINAN, Vigitel, Ambev, protection-reporting, calendar, and policy-event data.

## Published site

GitHub Pages deploys the `dashboard/` directory after each push to `main`. In the repository settings, set **Pages > Build and deployment > Source** to **GitHub Actions**.

## Refreshing dashboard data

The live site uses the checked-in aggregate files in `dashboard/data/`; it does not publish the local DuckDB database. To refresh them locally, run `work/export_dashboard_data.py` against the project database. The exporter applies `work/create_capstone_dashboard_views.sql` first.

## Vigitel comparability

The dashboard deliberately displays a gap for 2022 because no Vigitel collection occurred. It also displays the legacy current-drinking indicator as unavailable for 2024: the supplied 2024 data does not populate the prior 30-day source field, and the available past-12-month and frequency fields are not substituted as though they were comparable.
