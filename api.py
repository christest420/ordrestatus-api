import os
import asyncio
from flask import Flask, request, Response
from botbuilder.schema import Activity
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext
)

# Konfigurasjon fra miljøvariabler
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Oppsett av adapter og bot
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# EchoBot – svarer med samme tekst som du sender
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            await turn_context.send_activity(f"Echo: {turn_context.activity.text}")

bot = EchoBot()

# Flask-app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot API kjører OK!"

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_bot():
        await adapter.process_activity(activity, auth_header, bot.on_turn)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(call_bot())
    return Response(status=202)

# Kjør kun lokalt, ikke i produksjon
if __name__ == "__main__":
    app.run(debug=True, port=8000)
