import pandas as pd
from snowflake_connect import query_to_df, get_connection
from ydata_profiling import ProfileReport

covid = query_to_df("""
    SELECT COUNTRY_REGION, DATE,
           SUM(CASE WHEN CASE_TYPE = 'Confirmed' THEN CASES ELSE 0 END) AS CASES,
           SUM(CASE WHEN CASE_TYPE = 'Deaths' THEN CASES ELSE 0 END) AS DEATHS,
           SUM(CASE WHEN CASE_TYPE = 'Recovered' THEN CASES ELSE 0 END) AS RECOVERED,
           SUM(CASE WHEN CASE_TYPE = 'Active' THEN CASES ELSE 0 END) AS ACTIVE
    FROM COVID19_EPIDEMIOLOGICAL_DATA.PUBLIC.JHU_COVID_19
    GROUP BY COUNTRY_REGION, DATE
""")

covid[["CASES", "DEATHS", "RECOVERED", "ACTIVE"]] = covid[["CASES", "DEATHS", "RECOVERED", "ACTIVE"]].astype(float)

pop = pd.read_csv("python/etl/data/population.csv")
pop = pop.rename(columns={"pop2023": "population"})
pop = pop.drop_duplicates(subset="country")
merged = covid.merge(pop, left_on="COUNTRY_REGION", right_on="country", how="left")
merged["cases_per_100k"] = merged["CASES"] / merged["population"] * 100_000
merged["deaths_per_100k"] = merged["DEATHS"] / merged["population"] * 100_000

conn = get_connection()
from snowflake.connector.pandas_tools import write_pandas
write_pandas(conn, merged, table_name="COVID_ENRICHED", auto_create_table=True, overwrite=True)
conn.close()
print("Enriched table COVID_ENRICHED created with", len(merged), "rows")

ProfileReport(merged, title="COVID Enriched EDA").to_file("docs/eda_report.html")