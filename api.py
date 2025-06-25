import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, ConversationReference

app = Flask(__name__)
CORS(app)

# Bot Framework adapter settings
adapter_settings = BotFrameworkAdapterSettings("", "")
adapter = BotFrameworkAdapter(adapter_settings)

# Lagre conversation references
CONVERSATION_REFERENCES = {}

@app.route("/api/messages", methods=["POST"])
def messages():
    activity = Activity().deserialize(request.json)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context: TurnContext):
        user_input = turn_context.activity.text.strip()

        # Last inn CSV med semikolon som separator
        try:
            df = pd.read_csv("ordreinfobot.csv", sep=";")
        except Exception as e:
            await turn_context.send_activity(f"Feil ved lesing av ordreinfobot.csv: {e}")
            return

        # Sjekk om ordrenummer finnes
        rad = df[df["ordrenummer"].str.upper() == user_input.upper()]
        if not rad.empty:
            r = rad.iloc[0]
            response = (
                f"📦 Ordre: {r['ordrenummer']}\n"
                f"✅ Status: {r['status']}\n"
                f"📅 Bekreftet sendingsdato: {r['bekreftetSendingsdato']}\n"
                f"📋 Siste hendelser: {r['sisteHendelser']}"
            )
        else:
            response = f"Fant ingen ordre som matcher '{user_input}'."

        await turn_context.send_activity(response)

    task = adapter.process_activity(activity, auth_header, aux_func)
    return "", 202

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Bot kjører OK", "bruk": "Send POST til /api/messages"})

if __name__ == "__main__":
    app.run(debug=True)
