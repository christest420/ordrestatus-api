import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    ConversationState,
    MemoryStorage,
)
from botbuilder.core import ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity
from botbuilder.core.integration.aiohttp import BotFrameworkHttpClient, aiohttp_error_middleware
from botbuilder.core.skills import SkillConversationIdFactory
from botbuilder.integration.aiohttp.skills import SkillHandler

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

auth_config = ConfigurationBotFrameworkAuthentication(
    {"MicrosoftAppId": APP_ID, "MicrosoftAppPassword": APP_PASSWORD}
)

# Dummy Echo bot for testing
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            await turn_context.send_activity(Activity(type="message", text=f"Echo: {turn_context.activity.text}"))

bot = EchoBot()

async def messages_handler(request: web.Request) -> web.Response:
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")
    adapter = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
    context = TurnContext(adapter, activity)

    await bot.on_turn(context)
    return web.Response(status=200)

app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages_handler)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
