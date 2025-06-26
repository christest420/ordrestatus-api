import os
from aiohttp import web
from botbuilder.schema import Activity
from botbuilder.core import TurnContext
from botbuilder.integration.aiohttp import (
    CloudAdapter,
    ConfigurationBotFrameworkAuthentication
)


# Auth config
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

auth_config = ConfigurationBotFrameworkAuthentication(APP_ID, APP_PASSWORD)
adapter = CloudAdapter(auth_config)

# Handler-funksjon
async def handle_message(context: TurnContext):
    text = context.activity.text.strip()
    await context.send_activity(f"Du skrev: '{text}' (via aiohttp og CloudAdapter)")

# aiohttp POST route
async def messages_handler(request: web.Request) -> web.Response:
    body = await request.json()
    activity = Activity().deserialize(body)

    async def turn_handler(context: TurnContext):
        await handle_message(context)

    await adapter.process_activity(activity, "", turn_handler)
    return web.Response(status=200)

# Helsecheck
async def index_handler(request):
    return web.Response(text="Bot API kjører (aiohttp + CloudAdapter)")

# aiohttp setup
app = web.Application()
app.router.add_post("/api/messages", messages_handler)
app.router.add_get("/", index_handler)
