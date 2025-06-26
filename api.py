from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
import asyncio
import os

app = Flask(__name__)

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# EchoBot-logikk
async def echo_bot_logic(turn_context: TurnContext):
    if turn_context.activity.type == "message":
        await turn_context.send_activity(f"Echo: {turn_context.activity.text}")
    else:
        await turn_context.send_activity(f"[{turn_context.activity.type} event detected]")

@app.route("/", methods=["GET"])
def health_check():
    return "Bot API kjører OK!"

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Unsupported Media Type"}), 415

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task = loop.create_task(
        adapter.process_activity(activity, auth_header, echo_bot_logic)
    )
    loop.run_until_complete(task)

    return "", 202
