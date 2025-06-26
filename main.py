import os
from aiohttp import web
from botbuilder.core import (
    TurnContext,
    Configuration,
    MemoryStorage,
    ConversationState
)
from botbuilder.schema import Activity
from botbuilder.integration.aiohttp import (
    aiohttp_error_middleware,
    BotFrameworkHttpClient,
    BotFrameworkHttpAdapter
)
from botbuilder.core import ConfigurationBotFrameworkAuthentication

# Miljøvariabler fra Azure App Service
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

# Sett opp bot-authentisering med Azure App Registration-verdier
settings = Configuration()
settings["MicrosoftAppId"] = APP_ID
settings["MicrosoftAppPassword"] = APP_PASSWORD
auth_config = ConfigurationBotFrameworkAuthentication(settings)

# Bruk adapter med auth
adapter = BotFrameworkHttpAdapter(auth_config)

# Dummy bot som svarer med "Echo: <melding>"
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            await turn_context.send_activity(Activity(type="message", text=f"Echo: {turn_context.activity.text}"))

bot = EchoBot()

# HTTP handler for /api/messages
async def messages_handler(request: web.Request) -> web.Response:
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context: TurnContext):
        await bot.on_turn(turn_context)

    await adapter.process_activity(activity, auth_header, aux_func)
    return web.Response(status=200)

# Lag aiohttp-app og legg til route
app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages_handler)

# Kjør lokalt hvis ønskelig
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
