CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.policy_events (
    event_id VARCHAR PRIMARY KEY,
    event_date DATE NOT NULL,
    date_precision VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    legal_reference VARCHAR,
    description VARCHAR NOT NULL,
    verification_note VARCHAR,
    source_url VARCHAR NOT NULL
);

DELETE FROM analytics.policy_events
WHERE event_id IN (
    'carolina-dieckmann', 'next-minute', 'femicide-law', 'protective-order-breach',
    'mariana-ferrer', 'nao-e-nao', 'femicide-package', 'deepfake-abuse',
    'vicarious-femicide', 'national-abuse-registry', 'joana-maranhao', 'henry-borel',
    'vulnerable-welfare-reform', 'liquor-ipi', 'selective-tax-pilot'
);

INSERT INTO analytics.policy_events VALUES
    ('carolina-dieckmann', DATE '2013-04-02', 'day', 'Violence against women', 'Carolina Dieckmann Law', 'Law 12,737/2012', 'Criminalized unauthorized access to computer devices; included as digital-abuse context.', 'Effective 120 days after official publication.', 'https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12737.htm'),
    ('next-minute', DATE '2013-08-01', 'day', 'Violence against women', 'Next Minute Law', 'Law 12,845/2013', 'Required immediate and comprehensive care for people subjected to sexual violence.', 'Publication-date marker.', 'https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12845.htm'),
    ('femicide-law', DATE '2015-03-09', 'day', 'Violence against women', 'Femicide Law', 'Law 13,104/2015', 'Classified gender-motivated killing of women as qualified homicide and a heinous crime.', 'Publication-date marker.', 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13104.htm'),
    ('protective-order-breach', DATE '2018-04-03', 'day', 'Violence against women', 'Breach of Protective Orders Law', 'Law 13,641/2018', 'Criminalized breach of urgent judicial protective orders under the Maria da Penha Law.', 'Publication-date marker.', 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13641.htm'),
    ('mariana-ferrer', DATE '2021-11-22', 'day', 'Violence against women', 'Mariana Ferrer Law', 'Law 14,245/2021', 'Restricted demeaning or offensive conduct toward victims and witnesses in sexual-violence proceedings.', 'Publication-date marker.', 'https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14245.htm'),
    ('nao-e-nao', DATE '2024-06-26', 'day', 'Violence against women', 'Nao e Nao Protocol', 'Law 14,786/2023', 'Created prevention and victim-support protocol for nightlife and entertainment venues.', 'Effective 180 days after official publication.', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14786.htm'),
    ('femicide-package', DATE '2024-10-09', 'day', 'Violence against women', 'Femicide Package Law', 'Law 14,994/2024', 'Expanded penalties and made femicide an autonomous criminal offense.', 'Publication-date marker.', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14994.htm'),
    ('deepfake-abuse', DATE '2025-04-01', 'month', 'Violence against women', 'Deepfakes Anti-Abuse Law', 'Law 15,123/2025', 'Introduced stronger penalties for psychological violence using manipulated audio or video.', 'Month-level marker supplied for the policy timeline; statutory effective date requires legal-source confirmation.', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15123.htm'),
    ('vicarious-femicide', DATE '2026-04-01', 'month', 'Violence against women', 'Vicarious Femicide Law', 'Law 15,384/2026', 'Added vicarious violence and related protections to the legal framework.', 'Month-level marker supplied for the policy timeline.', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15384.htm'),
    ('national-abuse-registry', DATE '2026-05-01', 'month', 'Violence against women', 'National Abuse Registry Law', 'Law 15,409/2026', 'Created a national registry of persons convicted of violence against women.', 'Month-level marker supplied for the policy timeline.', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2026/lei/l15409.htm'),
    ('joana-maranhao', DATE '2012-05-17', 'day', 'Vulnerable-population protection', 'Joana Maranhao Law', 'Law 12,650/2012', 'Changed limitation-period rules for sexual crimes against children and adolescents.', 'Corrected legal reference year: 2012, not 2015.', 'https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12650.htm'),
    ('henry-borel', DATE '2022-05-24', 'day', 'Vulnerable-population protection', 'Henry Borel Law', 'Law 14,344/2022', 'Created protective measures and criminal provisions for violence against children and adolescents.', 'Publication-date marker.', 'https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14344.htm'),
    ('vulnerable-welfare-reform', DATE '2025-07-01', 'month', 'Vulnerable-population protection', 'Vulnerable Welfare Reform', 'Law 15,163/2025', 'Increased penalties for mistreatment of vulnerable people, including children, older people, and people with disabilities.', 'Month-level marker supplied for the policy timeline; statutory effective date requires legal-source confirmation.', 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15163.htm'),
    ('liquor-ipi', DATE '2016-01-01', 'day', 'Alcohol tax and regulation', 'Liquor IPI Reform', 'Law 13,241/2015', 'Changed IPI treatment for specified alcoholic beverages.', 'Relevant tax treatment applies from 1 January 2016.', 'https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13241.htm'),
    ('selective-tax-pilot', DATE '2026-01-01', 'month', 'Alcohol tax and regulation', 'Selective Tax Phase-In', 'Tax reform implementation context', 'Timeline context for the Selective Tax pilot described as applying to products harmful to public health, including alcoholic beverages.', 'Month-level implementation-context marker supplied for the policy timeline; not a causal intervention estimate.', 'https://www.gov.br/fazenda/pt-br/acesso-a-informacao/acoes-e-programas/reforma-tributaria');

CREATE OR REPLACE VIEW analytics.vw_sinan_notifications_enriched AS
WITH parsed AS (
    SELECT
        TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE AS occurrence_date,
        DATE_TRUNC('month', TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE)::DATE AS occurrence_month,
        EXTRACT(YEAR FROM TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE)::INTEGER AS occurrence_year,
        SG_UF_OCOR AS incident_state_code,
        CASE SG_UF_OCOR
            WHEN 'AC' THEN 'Acre'
            WHEN 'AL' THEN 'Alagoas'
            WHEN 'AP' THEN 'Amapa'
            WHEN 'AM' THEN 'Amazonas'
            WHEN 'BA' THEN 'Bahia'
            WHEN 'CE' THEN 'Ceara'
            WHEN 'DF' THEN 'Federal District'
            WHEN 'ES' THEN 'Espirito Santo'
            WHEN 'GO' THEN 'Goias'
            WHEN 'MA' THEN 'Maranhao'
            WHEN 'MT' THEN 'Mato Grosso'
            WHEN 'MS' THEN 'Mato Grosso do Sul'
            WHEN 'MG' THEN 'Minas Gerais'
            WHEN 'PA' THEN 'Para'
            WHEN 'PB' THEN 'Paraiba'
            WHEN 'PR' THEN 'Parana'
            WHEN 'PE' THEN 'Pernambuco'
            WHEN 'PI' THEN 'Piaui'
            WHEN 'RJ' THEN 'Rio de Janeiro'
            WHEN 'RN' THEN 'Rio Grande do Norte'
            WHEN 'RS' THEN 'Rio Grande do Sul'
            WHEN 'RO' THEN 'Rondonia'
            WHEN 'RR' THEN 'Roraima'
            WHEN 'SC' THEN 'Santa Catarina'
            WHEN 'SP' THEN 'Sao Paulo'
            WHEN 'SE' THEN 'Sergipe'
            WHEN 'TO' THEN 'Tocantins'
            ELSE 'Unknown'
        END AS incident_state_name,
        CASE
            WHEN SG_UF_OCOR IN ('AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO') THEN 'North'
            WHEN SG_UF_OCOR IN ('AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'Northeast'
            WHEN SG_UF_OCOR IN ('DF', 'GO', 'MT', 'MS') THEN 'Center-West'
            WHEN SG_UF_OCOR IN ('ES', 'MG', 'RJ', 'SP') THEN 'Southeast'
            WHEN SG_UF_OCOR IN ('PR', 'RS', 'SC') THEN 'South'
            ELSE 'Unknown'
        END AS region_name,
        ID_MN_OCOR AS incident_municipality_code,
        CASE CS_SEXO
            WHEN 'F' THEN 'Female'
            WHEN 'M' THEN 'Male'
            WHEN 'I' THEN 'Unknown'
            ELSE 'Unknown'
        END AS victim_sex,
        CASE CS_RACA
            WHEN '1' THEN 'White'
            WHEN '2' THEN 'Black'
            WHEN '3' THEN 'Asian'
            WHEN '4' THEN 'Brown/Mixed'
            WHEN '5' THEN 'Indigenous'
            WHEN '9' THEN 'Unknown'
            ELSE 'Unknown'
        END AS victim_race,
        CASE
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                THEN TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER)
        END AS victim_age_years,
        CASE
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                 AND TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER) BETWEEN 0 AND 11 THEN '0-11'
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                 AND TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER) BETWEEN 12 AND 17 THEN '12-17'
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                 AND TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER) BETWEEN 18 AND 29 THEN '18-29'
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                 AND TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER) BETWEEN 30 AND 44 THEN '30-44'
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                 AND TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER) BETWEEN 45 AND 59 THEN '45-59'
            WHEN REGEXP_MATCHES(TRIM(NU_IDADE_N), '^4[0-9]{1,3}$')
                 AND TRY_CAST(SUBSTR(TRIM(NU_IDADE_N), 2) AS INTEGER) BETWEEN 60 AND 120 THEN '60+'
            ELSE 'Unknown'
        END AS victim_age_group,
        CASE LOCAL_OCOR
            WHEN '01' THEN 'Residence'
            WHEN '02' THEN 'Collective housing'
            WHEN '03' THEN 'School'
            WHEN '04' THEN 'Sports location'
            WHEN '05' THEN 'Bar or similar'
            WHEN '06' THEN 'Public road'
            WHEN '07' THEN 'Commerce/services'
            WHEN '08' THEN 'Industry/construction'
            WHEN '09' THEN 'Other'
            WHEN '99' THEN 'Unknown'
            ELSE 'Unknown'
        END AS place_of_occurrence,
        CASE OUT_VEZES
            WHEN '1' THEN 'Repeated'
            WHEN '2' THEN 'Not repeated'
            WHEN '9' THEN 'Unknown'
            ELSE 'Unknown'
        END AS repeated_violence,
        CASE AUTOR_ALCO
            WHEN '1' THEN 'Yes'
            WHEN '2' THEN 'No'
            WHEN '9' THEN 'Unknown'
            ELSE 'Unknown'
        END AS alcohol_status,
        CASE
            WHEN COALESCE(DEF_TRANS, '9') = '1'
              OR COALESCE(DEF_FISICA, '9') = '1'
              OR COALESCE(DEF_MENTAL, '9') = '1'
              OR COALESCE(DEF_VISUAL, '9') = '1'
              OR COALESCE(DEF_AUDITI, '9') = '1'
              OR COALESCE(TRAN_MENT, '9') = '1'
              OR COALESCE(TRAN_COMP, '9') = '1'
              OR COALESCE(DEF_OUT, '9') = '1'
              OR COALESCE(DEF_ESPEC, '9') = '1'
                THEN 'Any disability/disorder'
            WHEN COALESCE(DEF_TRANS, '9') = '2'
              OR COALESCE(DEF_FISICA, '9') = '2'
              OR COALESCE(DEF_MENTAL, '9') = '2'
              OR COALESCE(DEF_VISUAL, '9') = '2'
              OR COALESCE(DEF_AUDITI, '9') = '2'
              OR COALESCE(TRAN_MENT, '9') = '2'
              OR COALESCE(TRAN_COMP, '9') = '2'
              OR COALESCE(DEF_OUT, '9') = '2'
              OR COALESCE(DEF_ESPEC, '9') = '2'
                THEN 'None recorded'
            ELSE 'Unknown'
        END AS disability_status,
        EXTRACT(DOW FROM TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE) AS day_of_week_number,
        STRFTIME(TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE, '%A') AS day_of_week_name,
        CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END AS is_holiday,
        h.holiday_name,
        h.holiday_type,
        CASE
            WHEN h.holiday_date IS NOT NULL THEN 'Holiday'
            WHEN EXTRACT(DOW FROM TRY_STRPTIME(DT_OCOR, '%Y-%m-%d')::DATE) IN (0, 6) THEN 'Non-holiday weekend'
            ELSE 'Non-holiday weekday'
        END AS calendar_bucket,
        CASE
            WHEN LOCAL_OCOR = '01'
              OR REL_CONJ = '1'
              OR REL_EXCON = '1'
              OR REL_NAMO = '1'
              OR REL_EXNAM = '1'
              OR REL_PAI = '1'
              OR REL_MAE = '1'
              OR REL_PAD = '1'
              OR REL_MAD = '1'
              OR REL_FILHO = '1'
              OR REL_IRMAO = '1'
              OR REL_CUIDA = '1'
                THEN 1
            ELSE 0
        END AS is_domestic_family,
        CASE
            WHEN REL_CONJ = '1'
              OR REL_EXCON = '1'
              OR REL_NAMO = '1'
              OR REL_EXNAM = '1'
                THEN 1
            ELSE 0
        END AS is_ipv,
        REL_CONJ,
        REL_EXCON,
        REL_NAMO,
        REL_EXNAM,
        REL_PAI,
        REL_MAE,
        REL_PAD,
        REL_MAD,
        REL_FILHO,
        REL_IRMAO,
        REL_CUIDA,
        VIOL_FISIC,
        VIOL_PSICO,
        VIOL_TORT,
        VIOL_SEXU,
        VIOL_TRAF,
        VIOL_FINAN,
        VIOL_NEGLI,
        VIOL_INFAN,
        VIOL_LEGAL,
        VIOL_OUTR
    FROM sinan.raw_crime_data AS s
    LEFT JOIN analytics.brazil_holidays AS h
        ON TRY_STRPTIME(s.DT_OCOR, '%Y-%m-%d')::DATE = h.holiday_date
)
SELECT *
FROM parsed
WHERE occurrence_date BETWEEN DATE '2012-01-01' AND DATE '2025-12-31';

CREATE OR REPLACE VIEW analytics.vw_sinan_cohorted_notifications AS
SELECT
    'All SINAN violence notifications' AS cohort_name,
    'A' AS cohort_code,
    *
FROM analytics.vw_sinan_notifications_enriched
UNION ALL
SELECT
    'Domestic or family violence' AS cohort_name,
    'B' AS cohort_code,
    *
FROM analytics.vw_sinan_notifications_enriched
WHERE is_domestic_family = 1
UNION ALL
SELECT
    'Intimate partner violence' AS cohort_name,
    'C' AS cohort_code,
    *
FROM analytics.vw_sinan_notifications_enriched
WHERE is_ipv = 1;

CREATE OR REPLACE VIEW analytics.fact_sinan_violence_type_mentions AS
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type' AS dimension_name, 'Physical violence' AS dimension_value
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_FISIC = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Psychological violence'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_PSICO = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Torture'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_TORT = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Sexual violence'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_SEXU = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Trafficking'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_TRAF = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Financial/economic violence'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_FINAN = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Neglect/abandonment'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_NEGLI = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Child labor'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_INFAN = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Legal intervention'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_LEGAL = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Violence type', 'Other violence'
FROM analytics.vw_sinan_cohorted_notifications
WHERE VIOL_OUTR = '1';

CREATE OR REPLACE VIEW analytics.fact_sinan_relationship_mentions AS
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship' AS dimension_name, 'Current spouse/partner' AS dimension_value
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_CONJ = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Former spouse/partner'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_EXCON = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Current boyfriend/girlfriend'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_NAMO = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Former boyfriend/girlfriend'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_EXNAM = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Father'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_PAI = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Mother'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_MAE = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Stepfather'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_PAD = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Stepmother'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_MAD = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Child'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_FILHO = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Sibling'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_IRMAO = '1'
UNION ALL
SELECT cohort_name, cohort_code, occurrence_date, occurrence_month, occurrence_year, region_name, incident_state_code,
       victim_sex, victim_age_group, alcohol_status, 'Aggressor relationship', 'Caregiver'
FROM analytics.vw_sinan_cohorted_notifications
WHERE REL_CUIDA = '1';

-- Keeps the raw Vigitel fields intact while exposing dashboard-safe, documented indicators.
-- The legacy 30-day indicator cannot be reproduced from the populated 2024 source fields,
-- so it is intentionally null rather than converted into a synthetic estimate.
CREATE OR REPLACE VIEW analytics.vw_vigitel_alcohol_indicators AS
WITH years AS (
    SELECT year
    FROM generate_series(2006, 2024) AS series(year)
),
weighted AS (
    SELECT
        YEAR(ano) AS year,
        TRY_CAST(pesorake2025 AS DOUBLE) AS survey_weight,
        lower(trim(CAST("bebida alcoolica" AS VARCHAR))) AS legacy_current_alcohol,
        lower(trim(CAST("Consumo abusivo de alcool" AS VARCHAR))) AS abusive_alcohol
    FROM vigitel.respostas_powerbi
),
aggregated AS (
    SELECT
        year,
        COUNT(*) AS record_count,
        SUM(CASE
            WHEN year <> 2024
             AND legacy_current_alcohol IN ('sim', 'sim, mas não ultimo mês', 'não consumo', 'nunca consumi')
             AND isfinite(survey_weight)
            THEN survey_weight
        END) AS current_30_day_denominator_weight,
        SUM(CASE
            WHEN year <> 2024 AND legacy_current_alcohol = 'sim' AND isfinite(survey_weight)
            THEN survey_weight
        END) AS current_30_day_numerator_weight,
        SUM(CASE
            WHEN abusive_alcohol IN ('sim', 'nao') AND isfinite(survey_weight)
            THEN survey_weight
        END) AS abusive_denominator_weight,
        SUM(CASE
            WHEN abusive_alcohol = 'sim' AND isfinite(survey_weight)
            THEN survey_weight
        END) AS abusive_numerator_weight
    FROM weighted
    GROUP BY 1
)
SELECT
    years.year,
    COALESCE(aggregated.record_count, 0) AS record_count,
    CASE
        WHEN years.year = 2022 THEN 'not_collected'
        WHEN years.year = 2024 THEN 'not_comparable'
        ELSE 'available'
    END AS current_alcohol_status,
    CASE
        WHEN years.year = 2022 THEN 'No Vigitel collection occurred in 2022 after the contracted operation was interrupted.'
        WHEN years.year = 2024 THEN 'The legacy 30-day field is unpopulated in the supplied data. The 2024 questionnaire retains past-12-month alcohol use and frequency, but these do not reproduce the prior 30-day measure; the comparable series is deliberately unavailable.'
        ELSE 'Weighted legacy 30-day alcohol-use indicator derived from the bebida alcoolica field.'
    END AS current_alcohol_method_note,
    aggregated.current_30_day_numerator_weight
        / NULLIF(aggregated.current_30_day_denominator_weight, 0) AS weighted_current_alcohol_share,
    aggregated.abusive_numerator_weight
        / NULLIF(aggregated.abusive_denominator_weight, 0) AS weighted_abusive_alcohol_share
FROM years
LEFT JOIN aggregated USING (year)
ORDER BY years.year;
