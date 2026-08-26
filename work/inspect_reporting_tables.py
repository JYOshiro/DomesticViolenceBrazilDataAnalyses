import duckdb
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)

for query in [
    "DESCRIBE main.crimes_violencia_domestica",
    "SELECT * FROM main.crimes_violencia_domestica LIMIT 5",
    "SELECT COUNT(*) AS rows FROM main.crimes_violencia_domestica",
    "DESCRIBE sinan.raw_crime_data",
]:
    print(connection.sql(query).df().to_string(index=False))
    print()
