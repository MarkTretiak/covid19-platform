import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))
from snowflake_connect import query_to_df
from prophet import Prophet
import pandas as pd

def forecast_country(country, periods=30):
    df = query_to_df(f"""
        SELECT DATE as ds, CASES as y FROM COVID_ENRICHED
        WHERE COUNTRY_REGION = '{country}' ORDER BY DATE
    """)
    df.columns = df.columns.str.lower()
    df["y"] = df["y"].astype(float)
    df["ds"] = pd.to_datetime(df["ds"])
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)

if __name__ == "__main__":
    print(forecast_country("Lithuania"))