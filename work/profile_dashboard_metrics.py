import duckdb
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)

queries = [
    """
    SELECT MIN(incident_date) AS first_date, MAX(incident_date) AS last_date,
           COUNT(*) AS reports, COUNT(report_channel) AS identified_channels
    FROM main.crimes_violencia_domestica
    """,
    """
    SELECT SPLIT_PART(violation_type, '.', 1) AS major_type, COUNT(*) AS reports
    FROM main.crimes_violencia_domestica
    WHERE violation_type IS NOT NULL
    GROUP BY 1 ORDER BY 2 DESC LIMIT 12
    """,
    "SELECT AUTOR_ALCO, COUNT(*) AS notifications FROM sinan.raw_crime_data GROUP BY 1 ORDER BY 2 DESC",
    """
    SELECT
      SUM(CASE WHEN VIOL_FISIC = '1' THEN 1 ELSE 0 END) AS physical,
      SUM(CASE WHEN VIOL_PSICO = '1' THEN 1 ELSE 0 END) AS psychological,
      SUM(CASE WHEN VIOL_NEGLI = '1' THEN 1 ELSE 0 END) AS neglect,
      SUM(CASE WHEN VIOL_SEXU = '1' THEN 1 ELSE 0 END) AS sexual
    FROM sinan.raw_crime_data
    """,
]

for query in queries:
    print(connection.sql(query).df().to_string(index=False))
    print()
