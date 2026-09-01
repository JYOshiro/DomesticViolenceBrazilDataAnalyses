import json
import math
import csv
import os
from pathlib import Path

import duckdb

WORK_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORK_DIR.parent
COURSE_DIR = WORK_DIR.parents[2]
DATABASE = Path(
    os.environ.get(
        "CAPSTONE_DATABASE",
        r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    )
)
VIEWS_SQL = WORK_DIR / "create_capstone_dashboard_views.sql"
OUTPUT = PROJECT_DIR / "dashboard" / "data" / "dashboard-data.json"
SCRIPT_OUTPUT = PROJECT_DIR / "dashboard" / "data" / "dashboard-data.js"
LIGUE180_SOURCE = COURSE_DIR / "ligue180_2012_2019_official_annual_counts.csv"
PUBLIC_DATABASE_LABEL = "Python-analyses/banco_disque100.duckdb"

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


def read_ligue180_series():
    numeric_fields = {
        "year",
        "ligue180_total_contacts",
        "ligue180_violence_reports",
        "ligue180_formal_complaints",
        "ligue180_violence_related_total_recommended",
        "domestic_family_violence_count",
        "domestic_family_violence_pct",
    }
    rows = []
    with LIGUE180_SOURCE.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            parsed = {}
            for key, value in row.items():
                if key in numeric_fields:
                    parsed[key] = float(value) if value else None
                    if key == "year" and parsed[key] is not None:
                        parsed[key] = int(parsed[key])
                else:
                    parsed[key] = value
            rows.append(parsed)
    return rows


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

    breakdown_insights = run_query(
        connection,
        """
        SELECT
            year,
            cohort_code,
            cohort_name,
            region_name,
            dimension_name,
            dimension_value,
            COUNT(*) AS notification_count,
            SUM(CASE WHEN victim_age_years BETWEEN 0 AND 120 THEN victim_age_years ELSE 0 END) AS victim_age_sum,
            COUNT(*) FILTER (WHERE victim_age_years BETWEEN 0 AND 120) AS victim_age_known_count,
            COUNT(*) FILTER (WHERE victim_sex = 'Female') AS victim_sex_female_count,
            COUNT(*) FILTER (WHERE victim_sex = 'Male') AS victim_sex_male_count,
            COUNT(*) FILTER (WHERE victim_sex = 'Unknown') AS victim_sex_unknown_count,
            COUNT(*) FILTER (WHERE perpetrator_sex = 'Male') AS perpetrator_sex_male_count,
            COUNT(*) FILTER (WHERE perpetrator_sex = 'Female') AS perpetrator_sex_female_count,
            COUNT(*) FILTER (WHERE perpetrator_sex = 'Both sexes') AS perpetrator_sex_both_count,
            COUNT(*) FILTER (WHERE perpetrator_sex = 'Unknown') AS perpetrator_sex_unknown_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'No schooling/illiterate') AS schooling_none_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Grades 1-4 incomplete') AS schooling_grades_1_4_incomplete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Grade 4 complete') AS schooling_grade_4_complete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Grades 5-8 incomplete') AS schooling_grades_5_8_incomplete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Primary education complete') AS schooling_primary_complete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Secondary education incomplete') AS schooling_secondary_incomplete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Secondary education complete') AS schooling_secondary_complete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Higher education incomplete') AS schooling_higher_incomplete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Higher education complete') AS schooling_higher_complete_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Not applicable') AS schooling_not_applicable_count,
            COUNT(*) FILTER (WHERE victim_schooling = 'Unknown') AS schooling_unknown_count,
            COUNT(*) FILTER (WHERE REL_CONJ = '1') AS relationship_current_spouse_count,
            COUNT(*) FILTER (WHERE REL_EXCON = '1') AS relationship_former_spouse_count,
            COUNT(*) FILTER (WHERE REL_NAMO = '1') AS relationship_current_dating_count,
            COUNT(*) FILTER (WHERE REL_EXNAM = '1') AS relationship_former_dating_count,
            COUNT(*) FILTER (WHERE REL_PAI = '1') AS relationship_father_count,
            COUNT(*) FILTER (WHERE REL_MAE = '1') AS relationship_mother_count,
            COUNT(*) FILTER (WHERE REL_PAD = '1') AS relationship_stepfather_count,
            COUNT(*) FILTER (WHERE REL_MAD = '1') AS relationship_stepmother_count,
            COUNT(*) FILTER (WHERE REL_FILHO = '1') AS relationship_child_count,
            COUNT(*) FILTER (WHERE REL_IRMAO = '1') AS relationship_sibling_count,
            COUNT(*) FILTER (WHERE REL_CUIDA = '1') AS relationship_caregiver_count,
            COUNT(*) FILTER (WHERE VIOL_FISIC = '1') AS violence_physical_count,
            COUNT(*) FILTER (WHERE VIOL_PSICO = '1') AS violence_psychological_count,
            COUNT(*) FILTER (WHERE VIOL_TORT = '1') AS violence_torture_count,
            COUNT(*) FILTER (WHERE VIOL_SEXU = '1') AS violence_sexual_count,
            COUNT(*) FILTER (WHERE VIOL_TRAF = '1') AS violence_trafficking_count,
            COUNT(*) FILTER (WHERE VIOL_FINAN = '1') AS violence_financial_count,
            COUNT(*) FILTER (WHERE VIOL_NEGLI = '1') AS violence_neglect_count,
            COUNT(*) FILTER (WHERE VIOL_INFAN = '1') AS violence_child_labor_count,
            COUNT(*) FILTER (WHERE VIOL_LEGAL = '1') AS violence_legal_intervention_count,
            COUNT(*) FILTER (WHERE VIOL_OUTR = '1') AS violence_other_count
        FROM analytics.fact_sinan_breakdown_memberships
        GROUP BY 1, 2, 3, 4, 5, 6
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

    protection_profiles = run_query(
        connection,
        """
        WITH profiles AS (
            SELECT
                'Suspect gender' AS dimension_name,
                CASE
                    WHEN UPPER(suspect_gender) LIKE 'FEMIN%' THEN 'Female'
                    WHEN UPPER(suspect_gender) LIKE 'MASC%' THEN 'Male'
                    ELSE 'Unknown/other'
                END AS dimension_value
            FROM main.crimes_violencia_domestica

            UNION ALL

            SELECT
                'Victim gender',
                CASE
                    WHEN UPPER(victim_gender) LIKE 'FEMIN%' THEN 'Female'
                    WHEN UPPER(victim_gender) LIKE 'MASC%' THEN 'Male'
                    ELSE 'Unknown/other'
                END
            FROM main.crimes_violencia_domestica

            UNION ALL

            SELECT
                'Suspect relationship',
                CASE
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) = 'mae' THEN 'Mother'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) = 'pai' THEN 'Father'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE 'filho%' THEN 'Child'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE 'irmao%' THEN 'Sibling'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) = 'padrasto' THEN 'Stepfather'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) = 'madrasta' THEN 'Stepmother'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE 'neto%' THEN 'Grandchild'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) IN ('avo', 'avó') THEN 'Grandparent'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE 'tio%' THEN 'Aunt/uncle'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE 'sobrinho%' THEN 'Niece/nephew'
                    WHEN LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE '%companheiro%'
                      OR LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE '%marido%'
                      OR LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE '%namorado%'
                      OR LOWER(STRIP_ACCENTS(victim_suspect_relationship_normalized)) LIKE '%conjuge%'
                      THEN 'Current/former partner'
                    WHEN victim_suspect_relationship_normalized IS NULL THEN 'Unknown/other'
                    ELSE 'Other relationship'
                END
            FROM main.crimes_violencia_domestica

            UNION ALL

            SELECT
                'Violation group',
                CASE
                    WHEN LOWER(STRIP_ACCENTS(violation_type)) LIKE '%neglig%' THEN 'Neglect'
                    WHEN LOWER(STRIP_ACCENTS(violation_type)) LIKE '%psiqu%' THEN 'Psychological integrity'
                    WHEN LOWER(STRIP_ACCENTS(violation_type)) LIKE '%fisic%' THEN 'Physical integrity'
                    WHEN LOWER(STRIP_ACCENTS(violation_type)) LIKE '%sexual%' THEN 'Sexual violence'
                    WHEN LOWER(STRIP_ACCENTS(violation_type)) LIKE '%patrimon%' THEN 'Property/economic'
                    WHEN violation_type IS NULL THEN 'Unknown/other'
                    ELSE 'Other violation'
                END
            FROM main.crimes_violencia_domestica
        )
        SELECT dimension_name, dimension_value, COUNT(*) AS record_count
        FROM profiles
        GROUP BY 1, 2
        ORDER BY 1, 3 DESC, 2
        """,
    )

    ligue180_series = read_ligue180_series()
    reporting_method_changes = [
        {
            "year": 2014,
            "title": "Ligue 180 became a formal complaint channel",
            "detail": "From March 2014, the service moved beyond guidance and began receiving formal complaints.",
            "source": LIGUE180_SOURCE.name,
        },
        {
            "year": 2017,
            "title": "Reports and formal complaints were separated",
            "detail": "The official balance reports the two contact types separately, creating a break from earlier totals.",
            "source": LIGUE180_SOURCE.name,
        },
        {
            "year": 2018,
            "title": "Non-formal violence reports were converted",
            "detail": "After 12 June, non-formal reports were converted into formal complaints; the before-and-after categories should not be treated as identical.",
            "source": LIGUE180_SOURCE.name,
        },
        {
            "year": 2020,
            "title": "Combined protection extract changes scale around 2020-21",
            "detail": "The source-row series rises sharply from 2021 and continues at a different scale. With no stable report identifier or validated Disque 100/Ligue 180 split, the pre/post series is not treated as directly comparable.",
            "source": "main.crimes_violencia_domestica",
        },
    ]

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
            "database": PUBLIC_DATABASE_LABEL,
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
        "breakdownInsights": breakdown_insights,
        "calendarCounts": calendar_counts,
        "calendarDays": calendar_days,
        "weekdayCounts": weekday_counts,
        "weekdayDays": weekday_days,
        "holidaySummary": holiday_summary,
        "protectionYearly": protection_yearly,
        "protectionViolations": protection_violations,
        "protectionChannels": protection_channels,
        "protectionProfiles": protection_profiles,
        "ligue180Official": ligue180_series,
        "reportingMethodChanges": reporting_method_changes,
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
        f"{len(breakdowns)} breakdown rows, "
        f"{len(breakdown_insights)} breakdown insight rows, and "
        f"{len(protection_yearly)} protection yearly rows."
    )


if __name__ == "__main__":
    main()
