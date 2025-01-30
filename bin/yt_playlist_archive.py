#!/usr/bin/env python3
import argparse
import asyncio
import csv
import errno
import logging
import math
import os
import platform
import signal
import socket
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

import psutil
import requests
import telegram
from ratelimiter import RateLimiter
from telegram.request import HTTPXRequest
from yt_dlp import YoutubeDL

# region force single instance of the program
# source: https://stackoverflow.com/questions/63525619/how-can-i-disable-multiple-instances-of-a-python-script
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 12345
try:
    s.bind((host, port))  # Bind to the port
except OSError as os_error:
    if os_error.errno == errno.EADDRINUSE:
        print("Can't run multiple instances of the program at the same time.")
        exit(1)
    else:
        raise
print("Listening on %s:%d" % (host, port))
# endregion

LOGS_DIR = os.getenv('LOGS')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("YT_PLAYLIST_ARCHIVE_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("YT_PLAYLIST_ARCHIVE_TELEGRAM_BOT_CHAT_ID")
WAYBACK_MACHINE_COOLDOWN_REQUESTS = 15
WAYBACK_MACHINE_COOLDOWN_SECONDS = 1 * 60

script_basename = os.path.basename(__file__)
basename_root = os.path.splitext(script_basename)[0]
videos_dir = os.path.join(tempfile.gettempdir(), basename_root, datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

failed_ones = []

telegram_request = HTTPXRequest(connection_pool_size=20)
telegram_bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN, request=telegram_request)

# region uniquely identify the process
node = platform.uname().node  # hostname
pid = os.getpid()
process = psutil.Process(pid)
process_start = datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d_%H-%M-%S.%f')
metadata = f"[{node}#{process_start}#{pid}] "


# endregion


async def log_and_send_result(result: str):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    text = metadata + f"[{timestamp}] {result}. "

    if len(failed_ones) == 0:
        text += "Success."
    else:
        text += "Failed ones:\n" + "\n".join(map(lambda x: str(x), failed_ones))

    log.info(text)
    await send_telegram_message(text)


async def sign_handler_intermediary(_, __):
    await log_and_send_result("Aborted")
    loop = asyncio.get_event_loop()
    loop.stop()


def sigint_handler(signum, frame):
    asyncio.create_task(sign_handler_intermediary(signum, frame))


signal.signal(signal.SIGINT, sigint_handler)


def setup_logger():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_filename = os.path.join(LOGS_DIR, f'{basename_root}_{timestamp}.log')

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


log = setup_logger()


def rate_limiter_callback(until):
    duration = int(round(until - time.time()))
    till_string = f" (till {datetime.fromtimestamp(until).strftime('%Y-%m-%d_%H-%M-%S')})"
    log.info('Rate limited, sleeping for {:d} seconds'.format(duration) + till_string)


rate_limiter = RateLimiter(max_calls=WAYBACK_MACHINE_COOLDOWN_REQUESTS, period=WAYBACK_MACHINE_COOLDOWN_SECONDS,
                           callback=rate_limiter_callback)


def validate_natural_number(value):
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a natural number greater than 0.")
    return int_value


def split_file(file_path: str, split_size_in_bytes: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    number_of_parts = math.ceil(os.path.getsize(file_path) / split_size_in_bytes)
    part_number = 1
    file_paths = []

    with open(file_path, 'rb') as file:
        while chunk := file.read(split_size_in_bytes):
            file_name = os.path.basename(file_path) + f'_part-{part_number:02}-of-{number_of_parts}'
            output_file = os.path.join(output_dir, file_name)
            file_paths.append(output_file)
            with open(output_file, 'wb') as output:
                output.write(chunk)
            part_number += 1

    return file_paths


def delete_file(path: str):
    Path(path).unlink(missing_ok=True)


async def send_file_to_telegram(file_path: str, caption: str, on_failure: Callable[[Exception], None]):
    retries = 10

    for _ in range(retries):
        try:
            await telegram_bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=open(file_path, 'rb'), caption=caption)
            delete_file(file_path)
            return
        except Exception as e:
            if _ == retries - 1:
                on_failure(e)

                delete_file(file_path)
                return


async def download_video_and_send_to_telegram(position: int, title: str, url: str):
    # download using yt-dlp

    # https://github.com/yt-dlp/yt-dlp/#embedding-yt-dlp
    ydl_options = {
        'paths': {'home': videos_dir},
        'no_warnings': True,
        'retries': 50,
        'fragment_retries': 50,
        'restrictfilenames': True,
    }

    retries = 10
    for retry_number in range(retries + 1):
        if retry_number > 0:
            log.info(f"Retry {retry_number}/{retries} for downloading")
        try:
            with YoutubeDL(ydl_options) as ydl:
                # python yt-dlp get filename -> https://stackoverflow.com/a/78955109/17299754
                info_dict = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info_dict)

                # send to telegram

                # https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file
                # see test-telegram-bot-file-limit() for details (tested limit is between 52428400b and 52428600b)
                file_size_limit = 50 * (1000 ** 2)  # use 50 MB instead of 50 MiB because the latter fails
                file_size = os.path.getsize(file_path)

                if file_size < file_size_limit:
                    on_send_failure = lambda e: failed_ones.append(
                        (position, title, url, f"telegram bot api return exception: {e}"))
                    await send_file_to_telegram(file_path, f"{position}. {title} ({url})", on_failure=on_send_failure)
                else:
                    splits_paths = split_file(file_path, file_size_limit, file_path + '_splits')
                    for split_path in splits_paths:
                        split_name = os.path.basename(split_path)
                        on_send_failure = lambda e: failed_ones.append(
                            (position, split_name, url, f"telegram bot api return exception: {e}"))
                        await send_file_to_telegram(split_path, f"{position}. {split_name} ({url})",
                                                    on_failure=on_send_failure)
                return
        except Exception as yt_dlp_exception:
            if retry_number == retries - 1:
                failed_ones.append(
                    (position, title, url, title, url, f"yt-dlp failed with exception: {yt_dlp_exception}"))
                log.error(yt_dlp_exception)


async def save_to_wayback_machine(position: int, title: str, url: str):
    # !!! NOTE this doesn't save the video itself, just the metadata
    wayback_machine_save_url = f"https://web.archive.org/save/{url}"

    retries = 5
    for _ in range(retries):
        try:
            log.info('Before rate_limiter')
            with rate_limiter:
                log.info('Calling Wayback Machine API')
                request = requests.get(wayback_machine_save_url)
                if request.status_code != 200:
                    raise Exception(f"wayback machine api returned status code: {request.status_code}")
                log.info(f'Result: {request.url}')
                return
        except Exception as e:
            if _ == retries - 1:
                failed_ones.append((position, title, url, f"calling wayback machine api returned exception: {e}"))
                return


async def process_video(mode: str, position: int, title: str, url: str):
    # git grep "Private video" $(git rev-list --all -- custom/"2 add queue re.csv") -- custom/"2 add queue re.csv"
    if title in ["[Deleted video]", "[Private video]"]:
        failed_ones.append((position, title, url, "video is deleted/private"))
        return

    if mode == 'telegram':
        await download_video_and_send_to_telegram(position, title, url)
    elif mode == 'wayback-machine':
        await save_to_wayback_machine(position, title, url)
    elif mode == 'both':
        await asyncio.gather(download_video_and_send_to_telegram(position, title, url),
                             save_to_wayback_machine(position, title, url))
    else:
        raise Exception("Unknown mode")


async def send_telegram_message(text: str):
    retries = 30
    for _ in range(retries):
        try:
            await telegram_bot.send_message(TELEGRAM_CHAT_ID, text)
            return
        except Exception as e:
            if _ == retries - 1:
                raise e


async def read_and_process_csv(mode: str, playlist_csv_file: str, start_position: Optional[int],
                               end_position: Optional[int]):
    with open(playlist_csv_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        sent_file_name = False

        # Iterate through rows
        for position, row in enumerate(reader):
            if position == 0:
                continue
            if start_position is not None and position < start_position:
                continue
            if end_position is not None and position > end_position:
                break

            if not sent_file_name:
                text = f"Processing {playlist_csv_file} in mode {mode} from position {start_position} to {end_position}"
                await send_telegram_message(metadata + text)
                sent_file_name = True

            title = row[0]
            url = row[1]

            log.info(f'{position}. {title} ({url})')
            await process_video(mode, position, title, url)

    # log and send result
    await log_and_send_result("Finished")


async def main():
    parser = argparse.ArgumentParser(description="Process a playlist reference with optional start and end positions.")

    # Required arguments
    mode_list = ['telegram', 'wayback-machine', 'both']
    parser.add_argument(
        'mode',
        type=str,
        choices=mode_list,
        help=f"Action to perform. Must be one of: {mode_list}"
    )

    parser.add_argument("playlist_csv", type=str,
                        help="Path to a CSV file that contains the videos in the format: title;url (ex: created by yt-playlist-to-csv.sh)")

    # Optional arguments
    parser.add_argument(
        "--start_position",
        type=validate_natural_number,
        help="Start position as a natural number greater than 0 (optional)."
    )
    parser.add_argument(
        "--end_position",
        type=validate_natural_number,
        help="End position as a natural number greater than 0 (optional)."
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate the condition: start_position <= end_position
    if args.start_position and args.end_position:
        if args.start_position > args.end_position:
            parser.error("start_position must be less than or equal to end_position.")

    log.info(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
    log.info(f"mode: {args.mode}")
    log.info(f"playlist_csv: {args.playlist_csv}")
    if args.start_position:
        log.info(f"Start Position: {args.start_position}")
    if args.end_position:
        log.info(f"End Position: {args.end_position}")

    await read_and_process_csv(args.mode, args.playlist_csv, args.start_position, args.end_position)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as re:
        if str(re) != "Event loop stopped before Future completed.":
            raise
