from flask import Flask, request, jsonify
import pandas as pd
import re
from flask_cors import CORS
from datetime import datetime
import locale
import os

app = Flask(__name__)
CORS(app)

# Forsøk å sette norsk datoformat
try:
    locale.setlocale(locale.LC_TIME, 'Norwegian_Norway.1252')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'nb_NO.UTF-8')
    except:
        print("⚠️ Kunne ikke sette norsk datoformat.")

def load_dataframe():
    try:
        df = pd.read_csv(
            "ordreinfobot.csv",
            sep=",",
            dtype=str,
            header=None,
            names=["Ordrenr", "Kunderef", "Checkpoint", "Ordremetode", "Bekreftet leveringsdato", "Levert dato"]
        )
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        print(f"❌ Klarte ikke å laste CSV: {e}")
        return None

def formater_dato(dato_str):
    if dato_str and re.match(r"\d{4}-\d{2}-\d{2}", dato_str):
        dato = datetime.strptime(dato_str, "%Y-%m-%d")
        return dato.strftime("%d. %B %Y").capitalize()
    return dato_str

def finn_rader_med_referanse(df, referanse):
    treff = []
    for index, row in df.iterrows():
        kunderef = str(row['Kunderef']).lower().split()
        if referanse.lower() in kunderef:
            treff.append(row)
    return treff

def hent_siste_hendelse(checkpoint_full):
    hendelser = [h.strip() for h in checkpoint_full.split("-") if h.strip()]
    ekskluder = [
        "plukkliste opprettet", "plukkliste utskrevet", "ordre opprettet",
        "plukkliste slettet", "ordrelinje slettet", "leveranse godkjent til fakturering",
        "faktura produsert", "faktura utskrevet"
    ]
    hendelser = [h for h in hendelser if h.lower() not in ekskluder]
    return hendelser[-1] if hendelser else "Ingen nye hendelser"

@app.route('/ordrestatus', methods=['GET'])
def ordrestatus():
    referansenummer = request.args.get('ordrenummer', '').lower()
    df = load_dataframe()
    if df is None:
        return jsonify({"status": "feil", "melding": "CSV-data ikke tilgjengelig på server."}), 500

    treff = finn_rader_med_referanse(df, referansenummer)

    if len(treff) == 1:
        rad = treff[0]
        ordremetode = rad['Ordremetode']
        checkpoint = hent_siste_hendelse(rad['Checkpoint'])
        bekreftetDato = formater_dato(rad['Bekreftet leveringsdato'])
        levertDato = formater_dato(rad['Levert dato'])

        if levertDato:
            return jsonify({
                "referanse": referansenummer,
                "status": "Sendt fra fabrikk",
                "sisteHendelser": checkpoint,
                "bekreftetSendingsdato": levertDato
            })

        return jsonify({
            "referanse": referansenummer,
            "status": ordremetode,
            "sisteHendelser": checkpoint,
            "bekreftetSendingsdato": bekreftetDato
        })

    elif len(treff) > 1:
        return jsonify({"status": "feil", "melding": "Flere ordre med samme referansenummer funnet. Vennligst kontakt kundeservice."})

    else:
        return jsonify({"status": "Ordre ikke funnet"})

@app.route('/')
def root():
    return jsonify({"status": "API kjører. Bruk /ordrestatus?ordrenummer=XXXX for spørring."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
