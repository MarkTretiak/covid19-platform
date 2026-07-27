from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sys, os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analytics"))
from snowflake_connect import query_to_df
from python.analytics.forecasting import forecast_country
from pymongo import MongoClient
from dotenv import load_dotenv
from cache import cache

load_dotenv()
app = FastAPI(title="COVID-19 Platform API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

mongo = MongoClient(os.getenv("MONGO_URI")).covid_platform

@app.get("/metrics")
@cache(ttl=300)
def get_metrics(country: str = Query(...), start_date: str = "2020-01-01", end_date: str = "2022-12-31"):
    sql = f"""
        SELECT DATE, CASES, DEATHS, "cases_per_100k", "deaths_per_100k" FROM COVID_ENRICHED
        WHERE COUNTRY_REGION = '{country}' AND DATE BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY DATE
    """
    df = query_to_df(sql)
    return df.to_dict(orient="records")

@app.get("/annotations")
def get_annotations(country: str):
    docs = list(mongo.annotations.find({"country_region": country}, {"_id": 0}))
    return docs

@app.post("/annotations")
def add_annotation(payload: dict):
    mongo.annotations.insert_one(payload)
    return {"status": "saved"}

@app.get("/forecast")
@cache(ttl=600)
def get_forecast(country: str = Query(...), periods: int = 30):
    df = forecast_country(country, periods=periods)
    df["ds"] = df["ds"].astype(str)
    return df.to_dict(orient="records")