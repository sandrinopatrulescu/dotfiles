#!/usr/bin/env python3
"""
https://core.telegram.org/bots/tutorial -> https://gitlab.com/Athamaxy/telegram-bot-tutorial/-/blob/main/TutorialBot.py
"""
import logging
import os
import tempfile
from datetime import datetime

from telegram import Update, User
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from yt_dlp import YoutubeDL

# region environment variables
LOGS = os.getenv('LOGS')
BOT_TOKEN = os.getenv('YT_DLP_TELEGRAM_BOT_BOT_TOKEN')
WHITELIST_FILE = os.getenv('YT_DLP_TELEGRAM_BOT_WHITELIST_FILE')
# endregion


script_basename = os.path.basename(__file__)
basename_root = os.path.splitext(script_basename)[0]
videos_dir = os.path.join(tempfile.gettempdir(), basename_root)
os.makedirs(videos_dir, exist_ok=True)


def setup_logger():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(LOGS, f'{basename_root}_{timestamp}.log')

    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create handlers
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_user_info(user: User):
    return user.username, user.first_name, user.last_name


def can_user_access(user_id: int) -> bool:
    if WHITELIST_FILE is None:
        return True
    with open(WHITELIST_FILE, 'r') as f:
        whitelist = f.read().splitlines()
    return any(str(user_id) in line.split(',')[0] for line in whitelist)


def download_video(url: str) -> str:
    ydl_hook_dict = {}
    ydl_options = {'paths': {'home': videos_dir}, "progress_hooks": [lambda x: ydl_hook_dict.update(x)]}

    with YoutubeDL(ydl_options) as ydl:
        return_code = ydl.download(url)
        if return_code != 0:
            log.error('ydl_hook_dict: ' + str(ydl_hook_dict))
            raise Exception(f'Returned code {return_code}')
        # https://stackoverflow.com/questions/74157935/getting-the-file-name-of-downloaded-video-using-yt-dlp
        return ydl_hook_dict['info_dict']['_filename']


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    trace_id = (str(update.message.date.astimezone()).split('+')[0], user_id)
    chat_id = update.effective_chat.id

    log.info(f'{trace_id} {get_user_info(update.message.from_user)} wrote {update.message.text}')

    if not can_user_access(user_id):
        log.info(f'{trace_id} User not in whitelist')
        await context.bot.send_message(chat_id=chat_id, text='You are not allowed to use this bot')
        return

    try:
        video_path = download_video(update.message.text)
        await context.bot.send_document(chat_id=chat_id, document=open(video_path, 'rb'))
        log.info(f'{trace_id} Sent video {video_path}')
    except Exception as e:
        log.error(f'{trace_id} {e}')
        text = f'Failed to send video {update.message.text}: {e}'
        await context.bot.send_message(chat_id=chat_id, text=text)


log = setup_logger()
if __name__ == '__main__':
    log.info(f'Using whitelist file {WHITELIST_FILE}')

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()
