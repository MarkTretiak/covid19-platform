Collection: annotations
{
  "_id": ObjectId,
  "country_region": "Lithuania",
  "date": "2021-04-15",
  "metric": "cases",
  "comment": "Spike due to reporting backlog",
  "author": "user_id_or_name",
  "tags": ["anomaly", "reporting-lag"],
  "created_at": ISODate
}

Collection: user_preferences
{
  "_id": ObjectId,
  "user_id": "string",
  "default_country": "Lithuania",
  "favorite_metrics": ["cases_per_100k", "deaths_per_100k"],
  "dashboard_theme": "dark"
}

Collection: supplementary_sources
{
  "_id": ObjectId,
  "country_region": "Lithuania",
  "source_name": "WHO Situation Report",
  "url": "https://...",
  "note": "Alternative case count for cross-checking",
  "added_at": ISODate
}