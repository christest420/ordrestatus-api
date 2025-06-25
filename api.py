from flask import Flask, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Last inn CSV ved oppstart
CSV_FILE = "ordreinfobot.csv"
df = pd.read_csv(CSV_FILE, header=None, dtype=str)
df.fillna("", inplace=True)

@app.route("/", methods=["GET"])
def root():
    return "✅ API kjører!"

@app.route("/api/messages", methods=["POST"])
def messages():
    data = request.get_json()

    # Hent meldingen brukeren skrev
    user_input = ""
    try:
        user_input = data["text"].strip()
    except Exception:
        return {"type": "message", "text": "Beklager, jeg forstod ikke meldingen."}

    # Søk etter eksakt match i kolonne 1 eller 2
    match = df[(df[1] == user_input) | (df[1].str.contains(rf"\b{user_input}\b", na=False))]

    if match.empty:
        return {"type": "message", "text": f"Ingen ordre funnet for: {user_input}"}
    
    row = match.iloc[0]
    svar = (
        f"📦 Ordrestatus for {user_input}:\n\n"
        f"- Internreferanse: {row[0]}\n"
        f"- Kundeordre: {row[1]}\n"
        f"- Status: {row[2]}\n"
        f"- Produkt: {row[3]}\n"
        f"- Mottatt: {row[4]}\n"
        f"- Forventet sendt: {row[5]}"
    )

    return {"type": "message", "text": svar}
