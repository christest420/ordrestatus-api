import os
import pandas as pd
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, ConversationReference

app = Flask(__name__)

# Bot Framework adapter setup
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# CSV data (loaded once at startup)
CSV_PATH = os.path.join(os.path.dirname(__file__), "ordreinfobot.csv")

def search_csv(kunderef):
    try:
        df = pd.read_csv(CSV_PATH, header=None)
        for _, row in df.iterrows():
            if kunderef in str(row[1]):
                return (
                    f"Kunde: {row[0]}\n"
                    f"Kunderef: {row[1]}\n"
                    f"Status: {row[2]}\n"
                    f"Produkt: {row[3]}\n"
                    f"Bekreftet dato: {row[4]}\n"
                    f"Siste statusdato: {row[5]}"
                )
        return "Ingen treff"
    except Exception as e:
        return f"Feil ved lesing av CSV: {e}"

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)

    async def turn_call(turn_context: TurnContext):
        if activity.type == ActivityTypes.message:
            search_result = search_csv(activity.text.strip())
            await turn_context.send_activity(search_result)

    task = ADAPTER.process_activity(activity, "", turn_call)
    return Response(status=202)

@app.route("/", methods=["GET"])
def index():
    return "✅ Bot API kjører!"

if __name__ == "__main__":
    app.run(debug=True)
