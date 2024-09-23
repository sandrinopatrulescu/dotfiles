#!/usr/bin/env python3
import asyncio
import os
import sys

import telegram

RETRIES = 5
BOT_TOKEN = os.getenv("NOTIFY_TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("NOTIFY_TELEGRAM_BOT_CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)


async def run():
    if sys.argv[1] == '-m':
        await bot.send_message(chat_id=CHAT_ID, text=sys.argv[2])
    else:
        for _ in range(RETRIES + 1):
            try:
                await bot.send_document(chat_id=CHAT_ID, document=open(sys.argv[1], 'rb'))
                return
            except telegram.error.TelegramError as e:
                if _ == RETRIES:
                    raise e


asyncio.run(run())
