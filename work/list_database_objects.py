import duckdb

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)
print(
    connection.sql(
        """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        ORDER BY table_schema, table_name
        """
    ).df().to_string(index=False)
)
