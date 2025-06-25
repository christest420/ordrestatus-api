from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def index():
    return "✅ API kjører!"

@app.route("/api/messages", methods=["POST"])
def messages():
    try:
        data = request.get_json()
        print("🔵 Mottatt data fra bot:", data)  # Debug: print hele meldingen

        if not data or "text" not in data:
            return jsonify({"status": "feil", "melding": "Ingen tekst mottatt."})

        query = data["text"].strip().upper()
        print(f"🔍 Brukerspørsmål: {query}")

        df = pd.read_csv("ordreinfobot.csv", sep=";")
        match = df[df["ordrenummer"] == query]

        if match.empty:
            print("⚠️ Ingen treff.")
            return jsonify({"status": "ikke funnet", "svar": f"Ingen ordre funnet for {query}."})

        row = match.iloc[0]
        response = {
            "status": "funnet",
            "ordrenummer": row["ordrenummer"],
            "sisteHendelser": row["sisteHendelser"],
            "bekreftetSendingsdato": row["bekreftetSendingsdato"]
        }
        print("✅ Svar klar:", response)
        return jsonify(response)

    except Exception as e:
        print("🔥 Feil i /api/messages:", e)
        return jsonify({"status": "feil", "melding": str(e)}), 500
