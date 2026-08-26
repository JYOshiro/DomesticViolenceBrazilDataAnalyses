import duckdb

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)
print(
    connection.sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'vigitel'
          AND table_name = 'respostas_powerbi'
          AND (
            lower(column_name) LIKE '%alcool%'
            OR lower(column_name) LIKE '%peso%'
            OR lower(column_name) LIKE '%ponder%'
          )
        """
    ).df().to_string(index=False)
)
