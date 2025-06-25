import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from dotenv import load_dotenv

# Last inn .env hvis det finnes
load_dotenv()

app = Flask(__name__)
CORS(app)

# === Bot Framework-adapter ===
SETTINGS = BotFrameworkAdapterSettings("", "")
ADAPTER = BotFrameworkAdapter(SETTINGS)


class OrderStatusBot:
    async def on_turn(self, turn_context: TurnContext):
        user_input = turn_context.activity.text.strip().upper()
        if not user_input:
            await turn_context.send_activity("⚠️ Jeg forstod ikke meldingen. Prøv igjen.")
            return

        # Finn CSV-filen i samme mappe som api.py
        csv_path = os.path.join(os.path.dirname(__file__), "ordreinfobot.csv")

        try:
            df = pd.read_csv(csv_path, sep=";")
        except Exception as e:
            await turn_context.send_activity(f"🚨 Klarte ikke å laste ordredata: {e}")
            return

        matching_row = df[df["ordrenummer"].str.upper() == user_input]
        if not matching_row.empty:
            row = matching_row.iloc[0]
            status = row["status"]
            dato = row["bekreftetSendingsdato"]
            hendelser = row["sisteHendelser"]
            response = f"📦 **Status for {user_input}**\n\n- Status: {status}\n- Bekreftet sendingsdato: {dato}\n- Siste hendelser: {hendelser}"
        else:
            response = f"❌ Fant ingen ordre som matcher '{user_input}'."

        await turn_context.send_activity(response)


BOT = OrderStatusBot()


@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    activity = Activity().deserialize(body)

    async def aux_func(turn_context):
        await BOT.on_turn(turn_context)

    task = ADAPTER.process_activity(activity, "", aux_func)
    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def root():
    return "✅ Flask API for ordrestatus kjører."

