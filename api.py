from flask import Flask, request, jsonify
from flask_cors import CORS
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity
import asyncio

# Flask-oppsett
app = Flask(__name__)
CORS(app)

# Hardkodet testdata
ordredata = {
    "SO123456": {
        "ordrenummer": "SO123456",
        "status": "Mottatt",
        "bekreftetSendingsdato": "2024-05-03",
        "sisteHendelser": "Mottatt-Kappet-Pakket",
    }
}

# Bot Framework Adapter uten auth (for testing uten App ID / Secret)
adapter_settings = BotFrameworkAdapterSettings(app_id="", app_password="")
adapter = BotFrameworkAdapter(adapter_settings)

# Helse-sjekk
@app.route("/", methods=["GET"])
def index():
    return "Bot API kjører OK!"

# Meldingshåndtering
@app.route("/api/messages", methods=["POST"])
async def messages():
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return jsonify({"error": "Innhold må være application/json"}), 400

    activity = Activity().deserialize(body)

    async def turn_handler(turn_context: TurnContext):
        bruker_input = turn_context.activity.text.strip().upper()
        respons = generer_svar(bruker_input)
        await turn_context.send_activity(respons)

    try:
        auth_header = request.headers.get("Authorization", "")
        await adapter.process_activity(activity, auth_header, turn_handler)
        return "", 202
    except Exception as e:
        print(f"Feil under melding: {e}")
        return jsonify({"error": str(e)}), 500

# Svarlogikk
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

# Gunicorn trenger entry point
if __name__ == "__main__":
    app.run(debug=True, port=5000)
