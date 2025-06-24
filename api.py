from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Last inn CSV-filen én gang ved oppstart
CSV_FILE = "ordreinfobot.csv"
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"{CSV_FILE} finnes ikke i roten av prosjektet.")

df = pd.read_csv(CSV_FILE, sep=";")

@app.route("/", methods=["GET"])
def index():
    return "✅ API kjører!"

@app.route("/ordre", methods=["GET"])
def ordreinfo():
    kunderef = request.args.get("kunderef")
    if not kunderef:
        return jsonify({"status": "error", "message": "Parametret 'kunderef' mangler."}), 400

    filtrert = df[df["kunderef"].astype(str).str.contains(kunderef, case=False, na=False)]

    if filtrert.empty:
        return jsonify({"status": "not_found", "message": f"Ingen ordre funnet for '{kunderef}'."})

    # Returner strukturert data
    siste = filtrert.sort_values("dato", ascending=False).iloc[0]
    hendelser = filtrert.sort_values("dato", ascending=False)[["dato", "checkpoint"]].head(5)

    return jsonify({
        "status": "ok",
        "kunderef": kunderef,
        "sisteHendelser": hendelser.to_dict(orient="records"),
        "bekreftetSendingsdato": siste.get("bekreftet_sendingsdato", "")
    })

