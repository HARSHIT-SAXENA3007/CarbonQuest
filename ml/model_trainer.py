import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def generate_cluster_labels(df, n_clusters, api_key):
    if not api_key:
        return {
            "cluster_labels": {str(i): f"Cluster {i}" for i in range(n_clusters)},
            "x_axis": "PCA 1",
            "y_axis": "PCA 2",
        }

    summaries = df.groupby("Cluster")[["transport_emission", "energy_emission", "food_emission", "shopping_emission"]].mean().round(2)
    prompt = f"""
You are an AI helping label carbon footprint clusters based on average monthly emissions.
Here is the average emissions data for each cluster:

{summaries.to_string()}

- Label each cluster with a short but meaningful name (max 3 words).
- Also suggest labels for the 2 PCA axes (representing the most variation in emissions).
- Return only a JSON object in this format:
{{
  "cluster_labels": {{
    "0": "label0",
    "1": "label1",
    "2": "label2"
  }},
  "x_axis": "X Axis Label",
  "y_axis": "Y Axis Label"
}}
"""

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        raw_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw_response)
    except Exception as exc:
        print("Gemini labeling failed:", str(exc))
        return {
            "cluster_labels": {str(i): f"Cluster {i}" for i in range(n_clusters)},
            "x_axis": "PCA 1",
            "y_axis": "PCA 2",
        }


def run_kmeans_clustering(csv_path="data/user_data.csv", n_clusters=3):
    if not os.path.exists(csv_path):
        return pd.DataFrame([{"Cluster": 0, "PCA1": 0.0, "PCA2": 0.0}])

    df = pd.read_csv(csv_path, on_bad_lines="skip")
    df.dropna(subset=["transport_emission", "energy_emission", "food_emission", "shopping_emission"], inplace=True)

    if df.empty:
        return pd.DataFrame([{"Cluster": 0, "PCA1": 0.0, "PCA2": 0.0}])

    features = df[["transport_emission", "energy_emission", "food_emission", "shopping_emission"]]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    effective_clusters = max(1, min(n_clusters, len(df)))
    kmeans = KMeans(n_clusters=effective_clusters, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(scaled_features)

    if len(df) < 2:
        df["PCA1"] = 0.0
        df["PCA2"] = 0.0
    else:
        pca = PCA(n_components=2)
        components = pca.fit_transform(scaled_features)
        df["PCA1"] = components[:, 0]
        df["PCA2"] = components[:, 1]

    labels_info = generate_cluster_labels(df, effective_clusters, GEMINI_API_KEY)
    cluster_names = labels_info.get("cluster_labels", {})
    x_label = labels_info.get("x_axis", "PCA 1")
    y_label = labels_info.get("y_axis", "PCA 2")

    plt.figure(figsize=(8, 6))
    for cluster_id in range(effective_clusters):
        cluster_data = df[df["Cluster"] == cluster_id]
        label = cluster_names.get(str(cluster_id), f"Cluster {cluster_id}")
        plt.scatter(cluster_data["PCA1"], cluster_data["PCA2"], label=label)

    plt.title("User Carbon Footprint Clusters")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plot_path = os.path.join(os.path.dirname(__file__), "..", "static", "cluster_plot.png")
    plt.savefig(plot_path, format="png")
    plt.close()

    return df
