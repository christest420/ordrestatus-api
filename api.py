from flask import Flask, request, jsonify
from flask_cors import CORS
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio
import os

# Flask-app
app = Flask(__name__)
CORS(app)

# Hardkodet testdata
ordredata = {
    "SO123456": {
        "ordrenummer": "SO123456",
        "status": "Mottatt",
        "bekreftetSendingsdato": "2024-05-03",
        "sisteHendelser": "Mottatt-Kappet-Pakket"
    },
    "IF7890": {
        "ordrenummer": "SO123456",
        "status": "Mottatt",
        "bekreftetSendingsdato": "2024-05-03",
        "sisteHendelser": "Mottatt-Kappet-Pakket"
    }
}

# Adapter for Bot Framework (uten autentisering)
adapter_settings = BotFrameworkAdapterSettings("", "")
adapter = BotFrameworkAdapter(adapter_settings)

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot API kjører OK!"

@app.route("/api/messages", methods=["POST"])
async def messages():
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return jsonify({"error": "Content-Type må være application/json"}), 400

    activity = Activity().deserialize(body)

    async def turn_call(turn_context: TurnContext):
        brukerinput = turn_context.activity.text.strip().upper()
        respons = generer_svar(brukerinput)
        await turn_context.send_activity(respons)

    try:
        auth_header = request.headers.get("Authorization", "")
        await adapter.process_activity(activity, auth_header, turn_call)
        return "", 202
    except Exception as e:
        print(f"[❌ Feil i behandling av melding]: {e}")
        return jsonify({"error": str(e)}), 500

def generer_svar(ordrenummer):
    if ordrenummer in ordredata:
        rad = ordredata[ordrenummer]
        return (
            f"📦 **Ordre {rad['ordrenummer']}**\n"
            f"✅ Status: {rad['status']}\n"
            f"📅 Bekreftet sendingsdato: {rad['bekreftetSendingsdato']}\n"
            f"🛠️ Hendelser: {rad['sisteHendelser']}"
        )
    else:
        return f"❌ Fant ingen ordre med nummer {ordrenummer}."
