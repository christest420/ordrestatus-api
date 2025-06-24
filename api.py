from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

CSV_FIL = "ordreinfobot.csv"

@app.route("/")
def index():
    return "✅ API kjører!"

@app.route("/ordre", methods=["GET"])
def ordreinfo():
    kunderef = request.args.get("kunderef", "").strip()
    if not kunderef:
        return jsonify({"status": "feil", "melding": "kunderef mangler"}), 400

    if not os.path.exists(CSV_FIL):
        return jsonify({"status": "feil", "melding": f"Filen '{CSV_FIL}' finnes ikke."}), 500

    try:
        df = pd.read_csv(CSV_FIL, delimiter=",", header=None)
    except Exception as e:
        return jsonify({"status": "feil", "melding": f"Kunne ikke lese CSV: {str(e)}"}), 500

    df.columns = ["ordre_id", "kunderef", "status", "kunde", "mottatt", "bekreftet"]

    # Sjekk om eksakt match finnes i noen del av kunderef-kolonnen
    def match_kunderef(kolonneverdi):
        deler = kolonneverdi.split()
        return kunderef in deler

    treff = df[df["kunderef"].apply(match_kunderef)]

    if treff.empty:
        return jsonify({
            "status": "ikke funnet",
            "sisteHendelser": [],
            "bekreftetSendingsdato": None
        })

    rad = treff.iloc[0]
    return jsonify({
        "status": "funnet",
        "sisteHendelser": rad["status"].split("-"),
        "bekreftetSendingsdato": rad["bekreftet"]
    })

if __name__ == "__main__":
    app.run()
