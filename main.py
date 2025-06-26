import os
from aiohttp import web
from botbuilder.schema import Activity
from botbuilder.core import TurnContext
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication
)

# Hent verdier fra miljø (Azure App Settings eller GitHub secrets)
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Opprett autentiseringsobjekt med navngitte argumenter
auth_config = ConfigurationBotFrameworkAuthentication(
    app_id=APP_ID,
    app_password=APP_PASSWORD
)

# Opprett adapter
adapter = CloudAdapter(auth_config)

# Din bot-logikk – svarer med det brukeren skrev
async def handle_message(context: TurnContext):
    user_text = context.activity.text.strip()
    await context.send_activity(f"Du skrev: '{user_text}'")

# POST /api/messages – brukes av Bot Framework
async def messages_handler(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        activity = Activity().deserialize(body)

        async def aux_func(turn_context: TurnContext):
            await handle_message(turn_context)

        await adapter.process_activity(activity, "", aux_func)
        return web.Response(status=200)
    except Exception as e:
        print(f"Feil i messages_handler: {e}")
        return web.Response(status=500)

# GET / – helse-endepunkt
async def index_handler(request):
    return web.Response(text="Bot API kjører (aiohttp + CloudAdapter)")

# Konfigurer aiohttp-app
app = web.Application()
app.router.add_post("/api/messages", messages_handler)
app.router.add_get("/", index_handler)
