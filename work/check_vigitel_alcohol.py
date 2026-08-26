import duckdb

connection = duckdb.connect(
    r"C:\Users\jessi\iCloudDrive\Master - MBA\2026_T2_DATA6000\Python-analyses\banco_disque100.duckdb",
    read_only=True,
)
for query in [
    '''
    SELECT "Consumo abusivo de alcool" AS alcohol_indicator, COUNT(*) AS records
    FROM vigitel.respostas_powerbi
    GROUP BY 1 ORDER BY 2 DESC
    ''',
    '''
    SELECT year(ano) AS year, COUNT(*) AS records,
           AVG(CASE WHEN "Consumo abusivo de alcool" = 'Sim' THEN 1.0 WHEN "Consumo abusivo de alcool" = 'Nao' THEN 0.0 END) AS unweighted_share,
           SUM((CASE WHEN "Consumo abusivo de alcool" = 'Sim' THEN 1.0 WHEN "Consumo abusivo de alcool" = 'Nao' THEN 0.0 END) * TRY_CAST(pesorake2025 AS DOUBLE))
             / NULLIF(SUM(TRY_CAST(pesorake2025 AS DOUBLE)), 0) AS weighted_share
    FROM vigitel.respostas_powerbi
    GROUP BY 1 ORDER BY 1
    ''',
    '''
    SELECT "bebida alcoolica" AS overall_alcohol_indicator, COUNT(*) AS records
    FROM vigitel.respostas_powerbi
    GROUP BY 1 ORDER BY 2 DESC
    ''',
    '''
    SELECT YEAR(ano) AS year,
           SUM(CASE WHEN lower("bebida alcoolica") = 'sim' THEN 1.0 WHEN lower("bebida alcoolica") = 'não' THEN 0.0 END * TRY_CAST(pesorake2025 AS DOUBLE))
             / NULLIF(SUM(CASE WHEN lower("bebida alcoolica") IN ('sim', 'não') THEN TRY_CAST(pesorake2025 AS DOUBLE) END), 0) AS weighted_share
    FROM vigitel.respostas_powerbi
    WHERE lower("bebida alcoolica") IN ('sim', 'não')
    GROUP BY 1 ORDER BY 1
    ''',
]:
    print(connection.sql(query).df().to_string(index=False))
    print()
