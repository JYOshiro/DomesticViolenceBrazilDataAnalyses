import duckdb

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)
print(
    connection.sql(
        """
        SELECT holiday_name, COUNT(*) AS incident_count
        FROM analytics.vw_sinan_incidents_daily
        WHERE holiday_name IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
        """
    ).df().to_string(index=False)
)
