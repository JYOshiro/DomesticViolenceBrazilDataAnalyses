import duckdb
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)

for query in [
    "SELECT report_channel, COUNT(*) AS reports FROM main.crimes_violencia_domestica GROUP BY 1 ORDER BY 2 DESC LIMIT 20",
    "DESCRIBE analytics.vw_sinan_incidents_daily",
]:
    print(connection.sql(query).df().to_string(index=False))
    print()
