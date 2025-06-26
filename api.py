# api.py
import os
import asyncio
from flask import Flask, request, Response
from botbuilder.core import (
    TurnContext,
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication
)
from botbuilder.schema import Activity

app = Flask(__name__)

# Hent credentials fra miljøvariabler
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Konfigurer autentisering
auth_config = ConfigurationBotFrameworkAuthentication(
    app_id=APP_ID,
    app_password=APP_PASSWORD
)

# Opprett CloudAdapter
adapter = CloudAdapter(auth_config)

# Enkel bot-logikk: svarer med samme tekst
async def handle_message(context: TurnContext):
    user_text = context.activity.text.strip()
    await context.send_activity(f"Du skrev: '{user_text}' (svar fra botten)")

@app.route("/", methods=["GET"])
def index():
    return "Bot API kjører OK!"

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers.get("Content-Type", ""):
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)

    async def aux_func(turn_context: TurnContext):
        await handle_message(turn_context)

    try:
        task = adapter.process_activity(activity, "", aux_func)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        return Response(status=200)
    except Exception as e:
        print(f"Feil i CloudAdapter: {e}")
        return Response(status=500)
