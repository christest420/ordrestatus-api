import asyncio
import pandas as pd
from flask import Flask, request, Response
from flask_cors import CORS
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    MessageFactory,
)
from botbuilder.schema import Activity
import os

# Konfigurasjon
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Bot og adapter
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Flask-app
app = Flask(__name__)
CORS(app)

# Bot-logikk
class StatusBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            user_input = turn_context.activity.text.strip().upper()
            response = self.svar_for_ordrenummer(user_input)
            await turn_context.send_activity(MessageFactory.text(response))

    def svar_for_ordrenummer(self, ordrenummer):
        try:
            df = pd.read_csv("ordreinfobot.csv", sep=";")
            if "ordrenummer" not in df.columns:
                return "⚠️ CSV-fil mangler kolonnen 'ordrenummer'."

            rad = df[df["ordrenummer"].str.upper() == ordrenummer]
            if rad.empty:
                return f"Fant ingen ordre med nummer: {ordrenummer}"

            status = rad.iloc[0].get("status", "Ukjent")
            bekreftet = rad.iloc[0].get("bekreftetSendingsdato", "Ukjent")
            siste = rad.iloc[0].get("sisteHendelser", "Ukjent")

            return (
                f"📦 Ordre: {ordrenummer}\n"
                f"📝 Status: {status}\n"
                f"📅 Sendes: {bekreftet}\n"
                f"🔄 Hendelser: {siste}"
            )
        except Exception as e:
            return f"🚨 Feil ved behandling av CSV: {e}"

# Opprett bot-instans
bot = StatusBot()

# Helse-sjekk
@app.route("/", methods=["GET"])
def index():
    return "Bot kjører OK"

# Meldings-endepunkt
@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" not in request.headers.get("Content-Type", ""):
        return Response(status=415)

    body = request.json
    activity = Activity().deserialize(body)

    async def call_bot():
        await adapter.process_activity(activity, "", bot.on_turn)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(call_bot())
        return Response(status=202)
    except Exception as e:
        print(f"Exception i /api/messages: {e}")
        return Response(status=500)
