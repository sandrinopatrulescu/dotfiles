#!/usr/bin/env python3
import asyncio
import os
import sys

import telegram

RETRIES = 5
BOT_TOKEN = os.getenv("BACKUPS_TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("BACKUPS_TELEGRAM_BOT_CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)


async def run():
    if sys.argv[1] == '-m':
        await bot.send_message(chat_id=CHAT_ID, text=sys.argv[2])
    else:
        for _ in range(RETRIES + 1):
            try:
                file = sys.argv[1]

                # https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file
                # see test-telegram-bot-file-limit() for details (tested limit is between 52428400b and 52428600b)
                byte_limit = 50 * (1024 ** 2)
                file_size = os.path.getsize(file)

                if file_size > byte_limit:
                    file_path = os.path.abspath(file)
                    message=f"[{file_path}] File size is {file_size} bytes, which is greater than the limit of {byte_limit} bytes. Please download it from the server."
                    await bot.send_message(chat_id=CHAT_ID, text=message)
                    print(message)
                    exit(1)

                await bot.send_document(chat_id=CHAT_ID, document=open(file, 'rb'))
                return
            except telegram.error.TelegramError as e:
                if _ == RETRIES:
                    raise e


asyncio.run(run())
