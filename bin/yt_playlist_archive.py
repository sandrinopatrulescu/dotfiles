#!/usr/bin/env python3
import argparse
import asyncio
import csv
import os
import tempfile
from pathlib import Path
from typing import Optional

import requests
import telegram
from ratelimiter import RateLimiter
from telegram.request import HTTPXRequest
from yt_dlp import YoutubeDL

TELEGRAM_BOT_TOKEN = os.getenv("YT_PLAYLIST_ARCHIVE_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("YT_PLAYLIST_ARCHIVE_TELEGRAM_BOT_CHAT_ID")
WAYBACK_MACHINE_COOLDOWN_SECONDS = 10 * 60

videos_dir = tempfile.gettempdir()
failed_ones = []

telegram_request = HTTPXRequest(connection_pool_size=20)
telegram_bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN, request=telegram_request)
rate_limiter = RateLimiter(max_calls=10, period=WAYBACK_MACHINE_COOLDOWN_SECONDS)


def validate_natural_number(value):
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a natural number greater than 0.")
    return int_value


async def send_video_to_telegram(position: int, title: str, url: str):
    # download using yt-dlp

    # https://github.com/yt-dlp/yt-dlp/#embedding-yt-dlp
    video_format = 'mp4'
    ydl_options = {'paths': {'home': videos_dir}, 'format': video_format, 'outtmpl': {'default': f'{title}.%(ext)s'},
                   'no_warnings': True}

    with YoutubeDL(ydl_options) as ydl:
        return_code = ydl.download(url)
        if return_code != 0:
            failed_ones.append((position, title, url, f"yt-dlp returned code {return_code}"))
            return

        file_path = os.path.join(videos_dir, f'{title}.{video_format}')

        # check file size

        # https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file
        # see test-telegram-bot-file-limit() for details (tested limit is between 52428400b and 52428600b)
        byte_limit = 50 * (1024 ** 2)
        file_size = os.path.getsize(file_path)

        if file_size > byte_limit:
            failed_ones.append((position, title, url, f"file too big ({file_size} bytes)"))
            return

        # send to telegram
        retries = 5
        delete_file = lambda: Path(file_path).unlink(missing_ok=True)

        for _ in range(retries):
            try:
                await telegram_bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=open(file_path, 'rb'),
                                                 caption=f"{position}. {title} ({url})")
                delete_file()
                return
            except Exception as e:
                if _ == retries - 1:
                    failed_ones.append((position, title, url, f"telegram bot api return exception: {e}"))
                    delete_file()
                    return


async def save_to_wayback_machine(position: int, title: str, url: str):
    wayback_machine_save_url = f"https://web.archive.org/save/{url}"


    retries = 5
    for _ in range(retries):
        try:
            print('Calling Wayback Machine API', end='...')
            # async with rate_limiter:
            with rate_limiter:
                request = requests.get(wayback_machine_save_url)
                if request.status_code != 200:
                    raise Exception(f"wayback machine api returned status code: {request.status_code}")
                print(f'Result: {request.url}')
                return
        except Exception as e:
            if _ == retries - 1:
                failed_ones.append((position, title, url, f"calling wayback machine api returned exception: {e}"))
                return


async def process_video(position: int, title: str, url: str):
    # git grep "Private video" $(git rev-list --all -- custom/"2 add queue re.csv") -- custom/"2 add queue re.csv"
    if title in ["[Deleted video]", "[Private video]"]:
        failed_ones.append((position, title, url, "video is deleted/private"))
        return

    await asyncio.gather(send_video_to_telegram(position, title, url), save_to_wayback_machine(position, title, url))


async def send_telegram_message(text: str):
    await telegram_bot.send_message(TELEGRAM_CHAT_ID, text)


async def read_and_process_csv(playlist_csv_file: str, start_position: Optional[int], end_position: Optional[int]):
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
                text = f"Processing {playlist_csv_file} from position {start_position} to {end_position}"
                await send_telegram_message(text)
                sent_file_name = True

            title = row[0]
            url = row[1]
            print(position, row)
            await process_video(position, title, url)

    # print and send failed_ones
    failed_ones_as_string = "Failed ones:\n" + "\n".join(map(lambda x: str(x), failed_ones))
    print("\n" + failed_ones_as_string)
    await send_telegram_message(failed_ones_as_string)


async def main():
    parser = argparse.ArgumentParser(description="Process a playlist reference with optional start and end positions.")

    # Required argument
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

    print(f"playlist_csv: {args.playlist_csv}")
    if args.start_position:
        print(f"Start Position: {args.start_position}")
    if args.end_position:
        print(f"End Position: {args.end_position}")

    await read_and_process_csv(args.playlist_csv, args.start_position, args.end_position)


if __name__ == "__main__":
    asyncio.run(main())
