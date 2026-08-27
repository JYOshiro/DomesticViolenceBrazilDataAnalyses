CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.vw_sinan_incidents_daily AS
WITH parsed AS (
    SELECT
        TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE AS occurrence_date,
        SG_UF_OCOR AS incident_state_code,
        ID_MN_OCOR AS incident_municipality_code,
        CS_SEXO AS victim_sex_code,
        CS_RACA AS victim_race_code,
        LOCAL_OCOR AS place_of_occurrence_code,
        AUTOR_SEXO AS perpetrator_sex_code,
        AUTOR_ALCO AS suspected_perpetrator_alcohol_use_code,
        VIOL_MOTIV AS violence_motivation_code,
        CASE
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                THEN TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER)
        END AS victim_age_years
    FROM sinan.raw_crime_data
), valid_dates AS (
    SELECT *
    FROM parsed
    WHERE occurrence_date BETWEEN
        (SELECT MIN(holiday_date) FROM analytics.brazil_holidays)
        AND (SELECT MAX(holiday_date) FROM analytics.brazil_holidays)
)
SELECT
    d.occurrence_date,
    DATE_TRUNC('month', d.occurrence_date)::DATE AS occurrence_month,
    STRFTIME(d.occurrence_date, '%Y-%m') AS occurrence_year_month,
    EXTRACT(DOW FROM d.occurrence_date) AS day_of_week_number,
    STRFTIME(d.occurrence_date, '%A') AS day_of_week_name,
    CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END AS is_holiday,
    h.holiday_name,
    h.holiday_type,
    d.incident_state_code,
    d.incident_municipality_code,
    d.victim_sex_code,
    d.victim_race_code,
    d.place_of_occurrence_code,
    d.perpetrator_sex_code,
    d.suspected_perpetrator_alcohol_use_code,
    d.violence_motivation_code,
    CASE
        WHEN d.victim_age_years BETWEEN 0 AND 120 THEN d.victim_age_years
    END AS victim_age_years
FROM valid_dates AS d
LEFT JOIN analytics.brazil_holidays AS h
    ON d.occurrence_date = h.holiday_date;

CREATE OR REPLACE VIEW analytics.vw_sinan_monthly_summary AS
WITH monthly_holidays AS (
    SELECT
        DATE_TRUNC('month', holiday_date)::DATE AS occurrence_month,
        COUNT(*) AS holidays_in_month,
        COUNT(*) FILTER (WHERE holiday_type = 'National Holiday') AS national_holidays_in_month
    FROM analytics.brazil_holidays
    GROUP BY 1
)
SELECT
    d.occurrence_month,
    d.occurrence_year_month,
    COUNT(*) AS incident_count,
    COUNT(DISTINCT d.occurrence_date) AS incident_days_in_month,
    SUM(d.victim_age_years) AS total_victim_age_years,
    AVG(d.victim_age_years) AS average_victim_age_years,
    COUNT(d.victim_age_years) AS incidents_with_valid_victim_age,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 0) AS incidents_sunday,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 1) AS incidents_monday,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 2) AS incidents_tuesday,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 3) AS incidents_wednesday,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 4) AS incidents_thursday,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 5) AS incidents_friday,
    COUNT(*) FILTER (WHERE d.day_of_week_number = 6) AS incidents_saturday,
    COALESCE(MAX(h.holidays_in_month), 0) AS holidays_in_month,
    COALESCE(MAX(h.national_holidays_in_month), 0) AS national_holidays_in_month,
    COUNT(*) FILTER (WHERE d.is_holiday = 1) AS incidents_on_holidays,
    COUNT(*) FILTER (
        WHERE d.is_holiday = 0
          AND d.day_of_week_number IN (0, 6)
    ) AS incidents_on_weekends,
    COUNT(*) FILTER (
        WHERE d.is_holiday = 0
          AND d.day_of_week_number BETWEEN 1 AND 5
    ) AS incidents_on_weekdays,
    COUNT(DISTINCT d.occurrence_date) FILTER (WHERE d.is_holiday = 1) AS holidays_with_incidents
FROM analytics.vw_sinan_incidents_daily AS d
LEFT JOIN monthly_holidays AS h
    ON d.occurrence_month = h.occurrence_month
GROUP BY
    d.occurrence_month,
    d.occurrence_year_month;

CREATE OR REPLACE VIEW analytics.vw_sinan_monthly_top3 AS
WITH dimension_counts AS (
    SELECT occurrence_month, occurrence_year_month, 'incident_state_code' AS dimension_name,
           COALESCE(NULLIF(TRIM(incident_state_code), ''), 'Unknown') AS dimension_value,
           COUNT(*) AS incident_count
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'incident_municipality_code',
           COALESCE(NULLIF(TRIM(incident_municipality_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'place_of_occurrence_code',
           COALESCE(NULLIF(TRIM(place_of_occurrence_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'victim_sex_code',
           COALESCE(NULLIF(TRIM(victim_sex_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'victim_race_code',
           COALESCE(NULLIF(TRIM(victim_race_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'perpetrator_sex_code',
           COALESCE(NULLIF(TRIM(perpetrator_sex_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'suspected_perpetrator_alcohol_use_code',
           COALESCE(NULLIF(TRIM(suspected_perpetrator_alcohol_use_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4

    UNION ALL

    SELECT occurrence_month, occurrence_year_month, 'violence_motivation_code',
           COALESCE(NULLIF(TRIM(violence_motivation_code), ''), 'Unknown'), COUNT(*)
    FROM analytics.vw_sinan_incidents_daily
    GROUP BY 1, 2, 3, 4
), ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY occurrence_month, dimension_name
            ORDER BY incident_count DESC, dimension_value
        ) AS rank_in_month
    FROM dimension_counts
)
SELECT
    occurrence_month,
    occurrence_year_month,
    dimension_name,
    dimension_value,
    incident_count,
    rank_in_month
FROM ranked
WHERE rank_in_month <= 3;

CREATE OR REPLACE VIEW analytics.vw_sinan_quarterly_ambev_summary AS
WITH sinan_quarterly AS (
    SELECT
        EXTRACT(YEAR FROM occurrence_month)::INTEGER AS year,
        EXTRACT(QUARTER FROM occurrence_month)::INTEGER AS quarter,
        DATE_TRUNC('quarter', occurrence_month)::DATE AS quarter_start_date,
        COUNT(*) AS months_in_quarter,
        SUM(incident_count) AS incident_count,
        SUM(incident_days_in_month) AS incident_days_in_quarter,
        SUM(total_victim_age_years) AS total_victim_age_years,
        SUM(incidents_with_valid_victim_age) AS incidents_with_valid_victim_age,
        SUM(total_victim_age_years)::DOUBLE
            / NULLIF(SUM(incidents_with_valid_victim_age), 0) AS average_victim_age_years,
        SUM(incidents_sunday) AS incidents_sunday,
        SUM(incidents_monday) AS incidents_monday,
        SUM(incidents_tuesday) AS incidents_tuesday,
        SUM(incidents_wednesday) AS incidents_wednesday,
        SUM(incidents_thursday) AS incidents_thursday,
        SUM(incidents_friday) AS incidents_friday,
        SUM(incidents_saturday) AS incidents_saturday,
        SUM(holidays_in_month) AS holidays_in_quarter,
        SUM(national_holidays_in_month) AS national_holidays_in_quarter,
        SUM(incidents_on_holidays) AS incidents_on_holidays,
        SUM(incidents_on_weekends) AS incidents_on_weekends,
        SUM(incidents_on_weekdays) AS incidents_on_weekdays,
        SUM(holidays_with_incidents) AS holidays_with_incidents
    FROM analytics.vw_sinan_monthly_summary
    GROUP BY 1, 2, 3
)
SELECT
    s.*,
    CONCAT(s.year, '-Q', s.quarter) AS year_quarter,
    a.beer_volume_sold_000_hl,
    a.brazil_beer_sales_tax_pct_gross_sales
FROM sinan_quarterly AS s
LEFT JOIN ambev.ambev_quarterly AS a
    ON s.year = a.year
   AND s.quarter = a.quarter;
