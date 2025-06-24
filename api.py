from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

CSV_PATH = os.path.join(os.path.dirname(__file__), 'ordreinfobot.csv')

@app.route("/ordre")
def ordre():
    kunderef = request.args.get("kunderef")
    if not kunderef:
        return jsonify({"status": "error", "message": "kunderef er påkrevd"}), 400

    try:
        df = pd.read_csv(CSV_PATH, header=None)
        df.columns = ["ordre_id", "kunderef", "status", "produkt", "mottatt_dato", "sendes_dato"]

        # Søk etter eksakt ord i kunderef-feltet
        match = df[df["kunderef"].apply(lambda x: kunderef in str(x).split())]

        if match.empty:
            return jsonify({"status": "not found", "kunderef": kunderef}), 404

        row = match.iloc[0]  # Tar første treff

        return jsonify({
            "status": "ok",
            "kunderef": row["kunderef"],
            "ordre_id": row["ordre_id"],
            "produkt": row["produkt"],
            "statusbeskrivelse": row["status"],
            "mottattDato": row["mottatt_dato"],
            "sendesDato": row["sendes_dato"]
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run()
