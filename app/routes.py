import os
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask import send_from_directory
from .emissions import calculate_emissions
from ml.model_trainer import run_kmeans_clustering

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

routes = Blueprint('routes', __name__)

def generate_suggestion_with_gemini(highest, emissions):
    prompt = f"""
You are an environmental expert. A user has the following monthly carbon emissions:
- Transport: {emissions['Transport']} kg CO₂
- Electricity: {emissions['Electricity']} kg CO₂
- Food: {emissions['Food']} kg CO₂
- Shopping: {emissions['Shopping']} kg CO₂

Their highest emission contributor is {highest}.
Give a detailed, actionable and comprehensive suggestions in 3 - 5 bullet points to help them reduce emissions in this area.
Use clear formatting with each point on a new line starting with • (bullet point).
Avoid repeating the category name.
Keep it practical and actionable.
"""
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        res = requests.post(endpoint, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("❌ Gemini API error:", str(e))
        return "⚠ Gemini AI failed to generate a suggestion."

def generate_cluster_summary_with_gemini(cluster_number, emissions):
    prompt = f"""
A user belongs to cluster {cluster_number} based on the following emission data:
- Transport: {emissions['Transport']} kg CO₂
- Electricity: {emissions['Electricity']} kg CO₂
- Food: {emissions['Food']} kg CO₂
- Shopping: {emissions['Shopping']} kg CO₂

There are 3 clusters:
Cluster 0: Eco-conscious users with low emissions.
Cluster 1: Moderate emitters with mixed behavior.
Cluster 2: High emitters with heavy lifestyle and consumption.

Explain what this user's cluster means.
Also explain what PCA 1 and PCA 2 on the axes represent in the cluster plot.
Keep it between concise and slightly detailed, beginner-friendly, and human-readable.
"""

    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        res = requests.post(endpoint, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("❌ Gemini cluster summary error:", str(e))
        return "⚠ Gemini AI failed to generate the cluster summary."

@routes.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    try:
        print("✅ Incoming data:", data)
        emissions, highest = calculate_emissions(data)

        entry = {
            'km': data['km'],
            'kwh': data['kwh'],
            'meat_meals': data['meat_meals'],
            'inr_spent': data['inr'],
            'transport_emission': emissions['Transport'],
            'energy_emission': emissions['Electricity'],
            'food_emission': emissions['Food'],
            'shopping_emission': emissions['Shopping']
        }

        df = pd.DataFrame([entry])
        df.to_csv('data/user_data.csv', mode='a', header=not os.path.exists('data/user_data.csv'), index=False)

        df_clustered = run_kmeans_clustering()
        user_cluster = int(df_clustered.iloc[-1]["Cluster"])

        suggestion = generate_suggestion_with_gemini(highest, emissions)
        cluster_summary = generate_cluster_summary_with_gemini(user_cluster, emissions)

        return jsonify({
            "emissions": emissions,
            "highest_contributor": highest,
            "suggested_action": suggestion,
            "cluster_summary": cluster_summary
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 400

@routes.route('/cluster-plot')
def get_cluster_plot():
    try:
        static_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
        file_path = os.path.join(static_folder_path, 'cluster_plot.png')

        if not os.path.exists(file_path):
            return jsonify({"error": "cluster_plot.png does not exist"}), 404

        return send_from_directory(directory=static_folder_path, path='cluster_plot.png', as_attachment=True)

    except Exception as e:
        return jsonify({"error": f"Image not found: {str(e)}"}), 404
