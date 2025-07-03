import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_cluster_labels(df, n_clusters, api_key):
    summaries = df.groupby('Cluster')[['transport_emission', 'energy_emission', 'food_emission', 'shopping_emission']].mean().round(2)
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

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        res = requests.post(endpoint, headers=headers, json=data)
        res.raise_for_status()
        raw_response = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        print("\n🔍 Gemini raw response:\n", raw_response)
        return json.loads(raw_response)
    except Exception as e:
        print("⚠ Gemini labeling failed:", str(e))
        return {
            "cluster_labels": {str(i): f"Cluster {i}" for i in range(n_clusters)},
            "x_axis": "PCA 1",
            "y_axis": "PCA 2"
        }

def run_kmeans_clustering(csv_path='data/user_data.csv', n_clusters=3):
    if not os.path.exists(csv_path):
        print("🚫 No data found. Run the calculator first.")
        return

    df = pd.read_csv(csv_path, on_bad_lines='skip')
    df.dropna(subset=['transport_emission', 'energy_emission', 'food_emission', 'shopping_emission'], inplace=True)

    X = df[['transport_emission', 'energy_emission', 'food_emission', 'shopping_emission']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)
    df['PCA1'] = components[:, 0]
    df['PCA2'] = components[:, 1]

    # ✅ Get meaningful cluster/axis labels
    labels_info = generate_cluster_labels(df, n_clusters, GEMINI_API_KEY)
    cluster_names = labels_info.get("cluster_labels", {})
    x_label = labels_info.get("x_axis", "PCA 1")
    y_label = labels_info.get("y_axis", "PCA 2")

    plt.figure(figsize=(8, 6))
    for i in range(n_clusters):
        cluster_data = df[df['Cluster'] == i]
        label = cluster_names.get(str(i), f"Cluster {i}")
        plt.scatter(cluster_data['PCA1'], cluster_data['PCA2'], label=label)

    plt.title("User Carbon Footprint Clusters")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plot_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'cluster_plot.png')
    plt.savefig(plot_path, format='png')
    plt.close()

    print("\n📊 Cluster Averages:")
    print(df.groupby('Cluster')[['transport_emission', 'energy_emission', 'food_emission', 'shopping_emission']].mean().round(2))
    return df
