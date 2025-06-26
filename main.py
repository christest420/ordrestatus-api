import os
from aiohttp import web
from botbuilder.schema import Activity
from botbuilder.core import (
    TurnContext,
    BotFrameworkAdapter,
    MemoryStorage,
    ConversationState,
    ConfigurationBotFrameworkAuthentication
)
from botbuilder.integration.aiohttp import BotFrameworkHttpClient, aiohttp_error_middleware

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

auth_config = ConfigurationBotFrameworkAuthentication({
    "MicrosoftAppId": APP_ID,
    "MicrosoftAppPassword": APP_PASSWORD
})

adapter = BotFrameworkAdapter(auth_config)
memory = MemoryStorage()
conversation_state = ConversationState(memory)


class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":
            await turn_context.send_activity(Activity(type="message", text=f"Echo: {turn_context.activity.text}"))


bot = EchoBot()


async def messages_handler(request: web.Request) -> web.Response:
    body = await request.json()
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context: TurnContext):
        await bot.on_turn(turn_context)

    await adapter.process_activity(activity, auth_header, aux_func)
    return web.Response(status=200)


app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages_handler)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8000)
