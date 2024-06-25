#!/usr/bin/env python3
"""
https://core.telegram.org/bots/tutorial -> https://gitlab.com/Athamaxy/telegram-bot-tutorial/-/blob/main/TutorialBot.py

kill -15 $(pgrep -f 'python3 /mnt/e/dotfiles/bin/yt_dlp_telegram_bot.py') && \
    xfce4-terminal -e 'bash -i -c "python3 /mnt/e/dotfiles/bin/yt_dlp_telegram_bot.py &"' && \
    sleep 1 && cd $LOGS && tail-follow-latest
"""
import logging
import os
import tempfile
from datetime import datetime

from telegram import Update, User
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from yt_dlp import YoutubeDL, DownloadError


def getenv_or_raise(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f'{name} environment variable is not set')
    return value


# region environment variables
LOGS = getenv_or_raise('LOGS')
BOT_TOKEN = getenv_or_raise('YT_DLP_TELEGRAM_BOT_BOT_TOKEN')
WHITELIST_FILE = os.getenv('YT_DLP_TELEGRAM_BOT_WHITELIST_FILE')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)
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
    logger.setLevel(LOG_LEVEL)

    # Create handlers
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(thread)d - %(name)s - %(levelname)s - %(message)s')
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


def download_video(url: str, name: str) -> str:
    # https://github.com/yt-dlp/yt-dlp/#embedding-yt-dlp
    video_format = 'mp4'
    ydl_options = {'paths': {'home': videos_dir}, 'format': video_format, 'outtmpl': {'default': f'{name}.%(ext)s'},
                   'logger': log, 'no_warnings': True}

    with YoutubeDL(ydl_options) as ydl:
        return_code = ydl.download(url)
        if return_code != 0:
            raise Exception(f'Returned code {return_code}')
        return os.path.join(videos_dir, f'{name}.{video_format}')


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    trace_id_date = str(update.message.date.astimezone()).split('+')[0].replace(':', '-').replace(' ', '_')
    trace_id = f'{trace_id_date}_{user_id}'
    chat_id = update.effective_chat.id

    log.info(f'{trace_id} {get_user_info(update.message.from_user)} wrote {update.message.text}')

    if not can_user_access(user_id):
        log.info(f'{trace_id} User not in whitelist')
        await context.bot.send_message(chat_id=chat_id, text='You are not allowed to use this bot')
        return

    try:
        video_path = download_video(update.message.text, trace_id)
        await context.bot.send_document(chat_id=chat_id, document=open(video_path, 'rb'))
        log.info(f'{trace_id} Sent video {video_path}')
    except Exception as e:
        if isinstance(e, DownloadError):
            pass
        else:
            log.exception(f'{trace_id}')
        await context.bot.send_message(chat_id=chat_id, text=f'Failed to send video {update.message.text}\n{e}')


log = setup_logger()
if __name__ == '__main__':
    log.info(f'Using whitelist file {WHITELIST_FILE}')

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()
