import json
import math
from pathlib import Path

import duckdb

WORK_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORK_DIR.parent
DATABASE = Path(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb"
)
VIEWS_SQL = WORK_DIR / "create_capstone_dashboard_views.sql"
OUTPUT = PROJECT_DIR / "dashboard" / "data" / "dashboard-data.json"
SCRIPT_OUTPUT = PROJECT_DIR / "dashboard" / "data" / "dashboard-data.js"

COHORT_DEFINITIONS = [
    {
        "code": "A",
        "name": "All SINAN violence notifications",
        "rule": "All violence notifications in SINAN with a valid occurrence date.",
    },
    {
        "code": "B",
        "name": "Domestic or family violence",
        "rule": "Residence location or a documented family/intimate relationship flag.",
    },
    {
        "code": "C",
        "name": "Intimate partner violence",
        "rule": "Current or former spouse/partner or boyfriend/girlfriend relationship flag.",
    },
]


def records(relation):
    return relation.df().to_dict(orient="records")


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def run_query(connection, query):
    return records(connection.sql(query))


def main():
    try:
        connection = duckdb.connect(str(DATABASE))
        connection.execute(VIEWS_SQL.read_text(encoding="utf-8"))
    except Exception:
        connection = duckdb.connect(str(DATABASE), read_only=True)

    monthly_cohort = run_query(
        connection,
        """
        SELECT
            occurrence_month,
            occurrence_year,
            cohort_code,
            cohort_name,
            region_name,
            COUNT(*) AS notification_count
        FROM analytics.vw_sinan_cohorted_notifications
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY 1, 3, 5
        """,
    )

    quarterly_cohort = run_query(
        connection,
        """
        SELECT
            DATE_TRUNC('quarter', occurrence_month)::DATE AS quarter_start_date,
            EXTRACT(YEAR FROM occurrence_month)::INTEGER AS year,
            EXTRACT(QUARTER FROM occurrence_month)::INTEGER AS quarter,
            CONCAT(EXTRACT(YEAR FROM occurrence_month), '-Q', EXTRACT(QUARTER FROM occurrence_month)) AS year_quarter,
            cohort_code,
            cohort_name,
            COUNT(*) AS notification_count
        FROM analytics.vw_sinan_cohorted_notifications
        GROUP BY 1, 2, 3, 4, 5, 6
        ORDER BY 1, 5
        """,
    )

    alcohol_monthly = run_query(
        connection,
        """
        SELECT
            occurrence_month,
            occurrence_year,
            cohort_code,
            cohort_name,
            region_name,
            SUM(CASE WHEN alcohol_status = 'Yes' THEN 1 ELSE 0 END) AS yes_count,
            SUM(CASE WHEN alcohol_status = 'No' THEN 1 ELSE 0 END) AS no_count,
            SUM(CASE WHEN alcohol_status = 'Unknown' THEN 1 ELSE 0 END) AS unknown_count,
            COUNT(*) AS notification_count
        FROM analytics.vw_sinan_cohorted_notifications
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY 1, 3, 5
        """,
    )

    breakdowns = run_query(
        connection,
        """
        WITH base_dimensions AS (
            SELECT occurrence_year AS year, cohort_code, cohort_name, region_name,
                   'Victim sex' AS dimension_name, victim_sex AS dimension_value, COUNT(*) AS notification_count
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'Victim age group', victim_age_group, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'Victim race/ethnicity', victim_race, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'Victim disability status', disability_status, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'Place of occurrence', place_of_occurrence, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'Repeated violence', repeated_violence, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'Region', region_name, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year, cohort_code, cohort_name, region_name,
                   'State', incident_state_name, COUNT(*)
            FROM analytics.vw_sinan_cohorted_notifications
            GROUP BY 1, 2, 3, 4, 5, 6
        ),
        mention_dimensions AS (
            SELECT occurrence_year AS year, cohort_code, cohort_name, region_name,
                   dimension_name, dimension_value, COUNT(*) AS notification_count
            FROM analytics.fact_sinan_violence_type_mentions
            GROUP BY 1, 2, 3, 4, 5, 6

            UNION ALL

            SELECT occurrence_year AS year, cohort_code, cohort_name, region_name,
                   dimension_name, dimension_value, COUNT(*) AS notification_count
            FROM analytics.fact_sinan_relationship_mentions
            GROUP BY 1, 2, 3, 4, 5, 6
        )
        SELECT *
        FROM (
            SELECT * FROM base_dimensions
            UNION ALL
            SELECT * FROM mention_dimensions
        )
        ORDER BY year, cohort_code, region_name, dimension_name, notification_count DESC, dimension_value
        """,
    )

    calendar_counts = run_query(
        connection,
        """
        SELECT
            occurrence_year AS year,
            cohort_code,
            cohort_name,
            region_name,
            calendar_bucket,
            COUNT(*) AS notification_count
        FROM analytics.vw_sinan_cohorted_notifications
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY 1, 2, 4, 5
        """,
    )

    calendar_days = run_query(
        connection,
        """
        WITH calendar_days AS (
            SELECT
                calendar_date AS holiday_date,
                CASE
                    WHEN h.holiday_date IS NOT NULL THEN 'Holiday'
                    WHEN EXTRACT(DOW FROM calendar_date) IN (0, 6) THEN 'Non-holiday weekend'
                    ELSE 'Non-holiday weekday'
                END AS calendar_bucket
            FROM GENERATE_SERIES(DATE '2012-01-01', DATE '2025-12-31', INTERVAL '1 day') AS d(calendar_date)
            LEFT JOIN analytics.brazil_holidays AS h
                ON d.calendar_date = h.holiday_date
        )
        SELECT EXTRACT(YEAR FROM holiday_date)::INTEGER AS year, calendar_bucket, COUNT(*) AS eligible_days
        FROM calendar_days
        GROUP BY 1, 2
        ORDER BY 1, 2
        """,
    )

    weekday_counts = run_query(
        connection,
        """
        SELECT
            occurrence_year AS year,
            cohort_code,
            cohort_name,
            region_name,
            day_of_week_name,
            COUNT(*) AS notification_count
        FROM analytics.vw_sinan_cohorted_notifications
        WHERE is_holiday = 0
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY 1, 2, 4, 5
        """,
    )

    weekday_days = run_query(
        connection,
        """
        WITH calendar_days AS (
            SELECT
                calendar_date AS holiday_date,
                STRFTIME(calendar_date, '%A') AS day_of_week_name,
                CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END AS is_holiday
            FROM GENERATE_SERIES(DATE '2012-01-01', DATE '2025-12-31', INTERVAL '1 day') AS d(calendar_date)
            LEFT JOIN analytics.brazil_holidays AS h
                ON d.calendar_date = h.holiday_date
        )
        SELECT EXTRACT(YEAR FROM holiday_date)::INTEGER AS year, day_of_week_name, COUNT(*) AS eligible_days
        FROM calendar_days
        WHERE is_holiday = 0
        GROUP BY 1, 2
        ORDER BY 1, 2
        """,
    )

    holiday_summary = run_query(
        connection,
        """
        WITH holiday_occurrences AS (
            SELECT
                EXTRACT(YEAR FROM holiday_date)::INTEGER AS year,
                holiday_name,
                COUNT(*) AS occurrences
            FROM analytics.brazil_holidays
            WHERE holiday_name IS NOT NULL
            GROUP BY 1, 2
        )
        SELECT
            n.occurrence_year AS year,
            n.cohort_code,
            n.cohort_name,
            n.region_name,
            n.holiday_name,
            COUNT(*) AS notification_count,
            MAX(o.occurrences) AS holiday_occurrences
        FROM analytics.vw_sinan_cohorted_notifications AS n
        LEFT JOIN holiday_occurrences AS o
            ON n.occurrence_year = o.year
           AND n.holiday_name = o.holiday_name
        WHERE n.holiday_name IS NOT NULL
        GROUP BY 1, 2, 3, 4, 5
        ORDER BY 1, 2, 4, 6 DESC, 5
        """,
    )

    protection_yearly = run_query(
        connection,
        """
        SELECT
            YEAR(incident_date) AS year,
            COUNT(*) AS report_count
        FROM main.crimes_violencia_domestica
        GROUP BY 1
        ORDER BY 1
        """,
    )

    protection_violations = run_query(
        connection,
        """
        SELECT
            YEAR(incident_date) AS year,
            SPLIT_PART(violation_type, '.', 1) AS violation_category,
            COUNT(*) AS report_count
        FROM main.crimes_violencia_domestica
        WHERE violation_type IS NOT NULL
        GROUP BY 1, 2
        ORDER BY 1, 3 DESC, 2
        """,
    )

    protection_channels = run_query(
        connection,
        """
        SELECT
            YEAR(incident_date) AS year,
            COALESCE(report_channel, 'Unknown') AS report_channel,
            COUNT(*) AS report_count
        FROM main.crimes_violencia_domestica
        GROUP BY 1, 2
        ORDER BY 1, 3 DESC, 2
        """,
    )

    vigitel = run_query(
        connection,
        """
        SELECT
            year,
            record_count,
            current_alcohol_status,
            current_alcohol_method_note,
            weighted_current_alcohol_share,
            weighted_abusive_alcohol_share
        FROM analytics.vw_vigitel_alcohol_indicators
        ORDER BY year
        """,
    )

    ambev = run_query(
        connection,
        """
        SELECT
            MAKE_DATE(year, ((quarter - 1) * 3) + 1, 1) AS quarter_start_date,
            year,
            quarter,
            CONCAT(year, '-Q', quarter) AS year_quarter,
            beer_volume_sold_000_hl,
            brazil_beer_sales_tax_pct_gross_sales
        FROM ambev.ambev_quarterly
        ORDER BY 1
        """,
    )

    policy_events = run_query(
        connection,
        """
        SELECT
            event_id,
            event_date,
            date_precision,
            event_type,
            title,
            legal_reference,
            description,
            verification_note,
            source_url
        FROM analytics.policy_events
        ORDER BY event_date, event_id
        """,
    )

    coverage = run_query(
        connection,
        """
        SELECT
            (SELECT MIN(occurrence_date) FROM analytics.vw_sinan_notifications_enriched) AS sinan_first_date,
            (SELECT MAX(occurrence_date) FROM analytics.vw_sinan_notifications_enriched) AS sinan_last_date,
            (SELECT MIN(incident_date) FROM main.crimes_violencia_domestica) AS protection_first_date,
            (SELECT MAX(incident_date) FROM main.crimes_violencia_domestica) AS protection_last_date,
            (SELECT MIN(YEAR(ano)) FROM vigitel.respostas_powerbi) AS vigitel_first_year,
            (SELECT MAX(YEAR(ano)) FROM vigitel.respostas_powerbi) AS vigitel_last_year,
            (SELECT MIN(year) FROM ambev.ambev_quarterly) AS ambev_first_year,
            (SELECT MAX(year) FROM ambev.ambev_quarterly) AS ambev_last_year
        """,
    )[0]

    payload = {
        "meta": {
            "refreshTimestamp": connection.sql(
                "SELECT CAST(CURRENT_TIMESTAMP AS VARCHAR)"
            ).fetchone()[0],
            "database": str(DATABASE),
            "coverage": coverage,
            "cohortDefinitions": COHORT_DEFINITIONS,
            "notes": [
                "Domestic/family violence uses residence or documented family/intimate relationship flags.",
                "Protection reports remain separate from SINAN notifications and are shown as a combined reporting signal because channel units are not validated as Disque 100 versus Ligue 180 in the available DuckDB table.",
                "Policy and tax events are contextual time markers. They do not estimate a legal or tax effect on notifications, reports, consumption, or sales.",
                "All browser datasets are aggregated; no row-level health records are exported.",
            ],
        },
        "monthlyCohort": monthly_cohort,
        "quarterlyCohort": quarterly_cohort,
        "alcoholMonthly": alcohol_monthly,
        "breakdowns": breakdowns,
        "calendarCounts": calendar_counts,
        "calendarDays": calendar_days,
        "weekdayCounts": weekday_counts,
        "weekdayDays": weekday_days,
        "holidaySummary": holiday_summary,
        "protectionYearly": protection_yearly,
        "protectionViolations": protection_violations,
        "protectionChannels": protection_channels,
        "vigitel": vigitel,
        "ambev": ambev,
        "policyEvents": policy_events,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(json_safe(payload), default=str)
    OUTPUT.write_text(serialized, encoding="utf-8")
    SCRIPT_OUTPUT.write_text(f"window.DASHBOARD_DATA = {serialized};\n", encoding="utf-8")
    print(
        "Wrote dashboard data with "
        f"{len(monthly_cohort)} monthly cohort rows, "
        f"{len(breakdowns)} breakdown rows, and "
        f"{len(protection_yearly)} protection yearly rows."
    )


if __name__ == "__main__":
    main()
