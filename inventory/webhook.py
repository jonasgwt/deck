#!/usr/bin/env python
# This program is dedicated to the public domain under the CC0 license.
# pylint: disable=import-error,unused-argument
"""
Simple example of a bot that uses a custom webhook setup and handles custom updates.
For the custom webhook setup, the libraries `Django` and `uvicorn` are used. Please
install them as `pip install Django~=4.2.4 uvicorn~=0.23.2`.
Note that any other `asyncio` based web server framework can be used for a custom webhook setup
just as well.

Usage:
Set bot Token, URL, admin CHAT_ID and PORT after the imports.
You may also need to change the `listen` value in the uvicorn configuration to match your setup.
Press Ctrl-C on the command line or send a signal to the process to stop the bot.
"""
import asyncio
import html
import json
import logging
from dataclasses import dataclass
from uuid import uuid4
from typing import Union

import uvicorn
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.urls import path

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
    
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define configuration constants
URL = "https://playground.nhhs-sjb.org/home/"
ADMIN_CHAT_ID = -1002125030997
PORT = 80 # 443, 80, 88, or 8443
TOKEN = "6879105065:AAE68ylp86mMmPnI8z9b41NKaR83vo4GgOE" 


@dataclass
class WebhookUpdate:

    user_id: int
    chat_id: Union[int, str]
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def start(update: Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot."""
    payload_url = html.escape(f"{URL}/submitpayload?user_id=<your user id>&payload=<payload>")
    text = (
        f"To check if the bot is still running, call <code>{URL}/healthcheck</code>.\n\n"
        f"To post a custom update, call <code>{payload_url}</code>."
    )
    await update.message.reply_html(text=text)

   

async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    
    chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    payloads = context.user_data.setdefault("payloads", [])
    payloads.append(update.payload)
    combined_payloads = "</code>\n• <code>".join(payloads)
    text = (
        f"The user {chat_member.user.mention_html()} has sent a new payload. "
        f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode=ParseMode.HTML)



async def telegram(request: HttpRequest) -> HttpResponse:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    await ptb_application.update_queue.put(
        Update.de_json(data=json.loads(request.body), bot=ptb_application.bot)
    )
    return HttpResponse()


async def custom_updates(request: HttpRequest) -> HttpResponse:
    """
    Handle incoming webhook updates by also putting them into the `update_queue` if
    the required parameters were passed correctly.
    """
    try:
        user_id = int(request.GET["user_id"])
        payload = request.GET["payload"]
    except KeyError:
        return HttpResponseBadRequest(
            "Please pass both `user_id` and `payload` as query parameters.",
        )
    except ValueError:
        return HttpResponseBadRequest("The `user_id` must be a string!")

    await ptb_application.update_queue.put(WebhookUpdate(user_id=user_id, payload=payload))
    return HttpResponse()



async def health(_: HttpRequest) -> HttpResponse:
    """For the health endpoint, reply with a simple plain text message."""
    return HttpResponse("The bot is still running fine :)")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ allow users to send noti to the grp from a channel """
# /notify Deletion delete
    CHANNELS = {
    "Deletion": -1002039591264,  
    "Expiry/Low qty": -1002134865986,  
    "Orders": -1002096563251,  
    "Loans & Returns": -1001924778677,  
     }
    try:
        channel_name = context.args[0].lower()  
        message_text = " ".join(context.args[1:])  

        if channel_name in CHANNELS:
            chat_id = CHANNELS[channel_name]
            await context.bot.send_message(chat_id=chat_id, text=message_text)

            response_text = f"Message sent to {channel_name} successfully!"
            await update.message.reply_text(response_text)
        else:
            response_text = "Invalid channel name."
            await update.message.reply_text(response_text)

    except IndexError:
        response_text = "Invalid usage. Provide channel name and message."
        await update.message.reply_text(response_text)


# Set up PTB application and a web application for handling the incoming requests.

context_types = ContextTypes(context=CustomContext)
# Here we set updater to None because we want our custom webhook server to handle the updates
# and hence we don't need an Updater instance
ptb_application = (
    Application.builder().token(TOKEN).updater(None).context_types(context_types).build()
)

# register handlers
ptb_application.add_handler(CommandHandler("start", start))
ptb_application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))
ptb_application.add_handler(CommandHandler("notify", notify))


urlpatterns = [
    path("telegram", telegram, name="Telegram updates"),
    path("submitpayload", custom_updates, name="custom updates"),
    path("healthcheck", health, name="health check"),
    path("notify", notify, name="notify"),
]
settings.configure(ROOT_URLCONF=__name__, SECRET_KEY=uuid4().hex)


async def main() -> None:
    """Finalize configuration and run the applications."""
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=get_asgi_application(),
            port=PORT,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    # Pass webhook settings to telegram
    await ptb_application.bot.set_webhook(url=f"{URL}/telegram", allowed_updates=Update.ALL_TYPES)

    # Run application and webserver together
    async with ptb_application:
        await ptb_application.start()
        await webserver.serve()
        await ptb_application.stop()


if __name__ == "__main__":
    asyncio.run(main())