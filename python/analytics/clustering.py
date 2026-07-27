import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "etl"))
from snowflake_connect import query_to_df
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt

df = query_to_df("""
    SELECT COUNTRY_REGION, MAX("cases_per_100k") AS peak_cases, MAX("deaths_per_100k") AS peak_deaths
    FROM COVID_ENRICHED GROUP BY COUNTRY_REGION
""")
df.columns = df.columns.str.lower()
df = df.dropna()
df[["peak_cases", "peak_deaths"]] = df[["peak_cases", "peak_deaths"]].astype(float)

X = StandardScaler().fit_transform(df[["peak_cases", "peak_deaths"]])
df["cluster"] = KMeans(n_clusters=4, random_state=42, n_init=10).fit_predict(X)

print(df.sort_values("cluster").to_string(index=False))
df.to_csv("docs/clusters.csv", index=False)
print("\nSaved to docs/clusters.csv")

plt.figure(figsize=(8, 6))
for c in sorted(df["cluster"].unique()):
    subset = df[df["cluster"] == c]
    plt.scatter(subset["peak_cases"], subset["peak_deaths"], label=f"Cluster {c}")
plt.xlabel("Peak cases per 100k")
plt.ylabel("Peak deaths per 100k")
plt.title("Country Clusters by COVID-19 Impact")
plt.legend()
plt.savefig("docs/cluster_scatter.png", dpi=150, bbox_inches="tight")
print("Saved docs/cluster_scatter.png")