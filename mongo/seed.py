import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.covid_platform

db.annotations.insert_one({
    "country_region": "Lithuania",
    "date": "2021-04-15",
    "metric": "cases",
    "comment": "Spike due to reporting backlog",
    "author": "mark",
    "tags": ["anomaly"]
})
print("Seeded.")