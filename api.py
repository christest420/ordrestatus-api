# api.py
from flask import Flask, request, Response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    TurnContext,
)
from botbuilder.schema import Activity
import asyncio
import os

app = Flask(__name__)

# Adapter setup med dummy app_id og password (bruk .env eller Azure secrets)
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# En enkel EchoBot som svarer med samme tekst
async def handle_message(context: TurnContext):
    user_text = context.activity.text.strip()
    await context.send_activity(f"Du skrev: '{user_text}' (svar fra botten)")

@app.route("/", methods=["GET"])
def index():
    return "Bot API kjører OK!"

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        json_message = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(json_message)

    async def aux_func(turn_context):
        await handle_message(turn_context)

    task = adapter.process_activity(activity, "", aux_func)
    try:
        asyncio.run(task)
        return Response(status=200)
    except Exception as e:
        print(f"Feil i /api/messages: {e}")
        return Response(status=500)

if __name__ == "__main__":
    app.run(debug=True)
