#!/usr/bin/env python3
import asyncio
import os
import sys

import telegram

BOT_TOKEN = os.getenv("BACKUPS_TELEGRAM_BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)


async def run():
    await bot.send_document(chat_id=os.getenv("BACKUPS_TELEGRAM_BOT_CHAT_ID"), document=open(sys.argv[1], 'rb'))


asyncio.run(run())
