import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request, send_from_directory

from .emissions import calculate_emissions

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.model_trainer import run_kmeans_clustering

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DATA_FILE = os.path.join("data", "user_data.csv")
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
PLOT_FILE = os.path.join(STATIC_DIR, "cluster_plot.png")

routes = Blueprint("routes", __name__)


def _fallback_suggestion(highest):
    suggestions = {
        "Transport": "Try reducing solo car trips, combining errands, and using public transport or cycling when possible.",
        "Electricity": "Cut standby power, use efficient appliances, and reduce heavy electricity usage during the month.",
        "Food": "Lowering meat-heavy meals and adding more plant-based meals is the most direct reduction lever here.",
        "Shopping": "Buy fewer new items, prioritize longer-lasting products, and avoid impulse purchases with high material footprint.",
    }
    return suggestions.get(highest, "Track your biggest category first and reduce it gradually with one practical habit change at a time.")


def _fallback_cluster_summary(cluster_number):
    return (
        f"Your data currently falls into cluster {cluster_number}. "
        "The plot groups users with similar emission patterns, while PCA 1 and PCA 2 are summary axes that compress the emission data into two dimensions."
    )


def _validate_payload(data):
    if not isinstance(data, dict):
        return None, "Request body must be valid JSON."

    required_fields = ("km", "kwh", "meat_meals", "inr")
    normalized = {}

    for field in required_fields:
        if field not in data:
            return None, f"Missing field: {field}"
        try:
            value = float(data[field])
        except (TypeError, ValueError):
            return None, f"Invalid numeric value for {field}"
        if value < 0:
            return None, f"{field} cannot be negative"
        normalized[field] = value

    normalized["meat_meals"] = int(normalized["meat_meals"])
    return normalized, None


def generate_suggestion_with_gemini(highest, emissions):
    if not GEMINI_API_KEY:
        return _fallback_suggestion(highest)

    prompt = f"""
You are an environmental expert. A user has the following monthly carbon emissions:
- Transport: {emissions["Transport"]} kg CO2
- Electricity: {emissions["Electricity"]} kg CO2
- Food: {emissions["Food"]} kg CO2
- Shopping: {emissions["Shopping"]} kg CO2

Their highest emission contributor is {highest}.
Give a detailed, actionable and comprehensive suggestions in 3 - 5 bullet points to help them reduce emissions in this area.
Use clear formatting with each point on a new line starting with a bullet.
Avoid repeating the category name.
Keep it practical and actionable.
"""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        print("Gemini API error:", str(exc))
        return _fallback_suggestion(highest)


def generate_cluster_summary_with_gemini(cluster_number, emissions):
    if not GEMINI_API_KEY:
        return _fallback_cluster_summary(cluster_number)

    prompt = f"""
A user belongs to cluster {cluster_number} based on the following emission data:
- Transport: {emissions["Transport"]} kg CO2
- Electricity: {emissions["Electricity"]} kg CO2
- Food: {emissions["Food"]} kg CO2
- Shopping: {emissions["Shopping"]} kg CO2

Explain what this user's cluster means.
Also explain what PCA 1 and PCA 2 on the axes represent in the cluster plot.
Keep it concise, beginner-friendly, and human-readable.
"""

    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as exc:
        print("Gemini cluster summary error:", str(exc))
        return _fallback_cluster_summary(cluster_number)


@routes.route("/api/calculate", methods=["POST"])
@routes.route("/calculate", methods=["POST"])
def calculate():
    data, error = _validate_payload(request.get_json(silent=True))
    if error:
        return jsonify({"error": error}), 400

    try:
        emissions, highest = calculate_emissions(data)
        entry = {
            "km": data["km"],
            "kwh": data["kwh"],
            "meat_meals_per_week": data["meat_meals"],
            "inr_spent": data["inr"],
            "transport_emission": emissions["Transport"],
            "energy_emission": emissions["Electricity"],
            "food_emission": emissions["Food"],
            "shopping_emission": emissions["Shopping"],
        }

        df = pd.DataFrame([entry])
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        df.to_csv(
            DATA_FILE,
            mode="a",
            header=not os.path.exists(DATA_FILE),
            index=False,
        )

        df_clustered = run_kmeans_clustering()
        user_cluster = int(df_clustered.iloc[-1]["Cluster"]) if not df_clustered.empty else 0

        suggestion = generate_suggestion_with_gemini(highest, emissions)
        cluster_summary = generate_cluster_summary_with_gemini(user_cluster, emissions)

        return jsonify(
            {
                "emissions": emissions,
                "highest_contributor": highest,
                "suggested_action": suggestion,
                "cluster_summary": cluster_summary,
                "plot_url": "/api/cluster-plot",
            }
        )
    except Exception as exc:
        print("Calculation error:", str(exc))
        return jsonify({"error": "Failed to calculate emissions."}), 400


@routes.route("/api/cluster-plot")
@routes.route("/cluster-plot")
def get_cluster_plot():
    try:
        if not os.path.exists(PLOT_FILE):
            return jsonify({"error": "cluster_plot.png does not exist"}), 404

        return send_from_directory(directory=STATIC_DIR, path="cluster_plot.png", as_attachment=True)
    except Exception as exc:
        return jsonify({"error": f"Image not found: {str(exc)}"}), 404
