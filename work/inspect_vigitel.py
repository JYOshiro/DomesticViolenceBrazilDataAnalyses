import duckdb
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)

for query in [
    "DESCRIBE vigitel.indicadores",
    "SELECT * FROM vigitel.indicadores LIMIT 10",
    "DESCRIBE vigitel.respostas_powerbi",
    "SELECT * FROM vigitel.respostas_powerbi LIMIT 5",
]:
    print(connection.sql(query).df().to_string(index=False))
    print()
