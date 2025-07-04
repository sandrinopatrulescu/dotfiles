#!/usr/bin/env python3
import datetime
import os
import subprocess
import sys

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SEPARATOR = ','
CSV_INDEX_URL = 0
CSV_INDEX_TITLE = 1


def read_file(videos_file_path):
    lines = open(videos_file_path, 'r').read().splitlines()
    if len(lines) > 0 and lines[0].startswith('videoId'):
        lines.pop(0)
    return list(map(lambda line: line.split(SEPARATOR), lines))


def get_youtube():
    client_secrets_file = os.path.join(os.environ['DOTS_SECRETS'], os.environ['YOUTUBE_API_OAUTH'])
    credentials_file_path = os.environ['YOUTUBE_API_CREDENTIALS_FILE_PATH']

    return get_youtube_from_client_secret(client_secrets_file, credentials_file_path)


def get_youtube_from_client_secret(client_secrets_file, credentials_file_path):
    # Sample Python code for youtube.playlistItems.insert
    # See instructions for running these code samples locally:
    # https://developers.google.com/explorer-help/code-samples#python

    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    # google_auth_oauthlib store credentials -> https://stackoverflow.com/questions/73485981/in-python-is-there-any-way-i-can-store-a-resource-object-so-i-can-use-it-late
    credentials = None
    if os.path.exists(credentials_file_path):
        credentials = Credentials.from_authorized_user_file(credentials_file_path, scopes)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            credentials = flow.run_local_server()

        credentials_file = open(credentials_file_path, 'w')
        credentials_file.write(credentials.to_json())

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


def create_request(youtube, playlist_id, video_id):
    return youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )


def strip_trailing_newline(string):
    return string[:-1] if string[-1] == '\n' else string


def test_unavailability(video_id):
    command = f'yt-dlp -s https://www.youtube.com/watch?v={video_id}'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _, stderr = process.communicate()
    exit_code = process.returncode

    if exit_code != 0:
        stderr_without_trailing_newline = strip_trailing_newline(stderr.decode('utf-8'))
        raise Exception(f'yt-dlp failed with exit code {exit_code} and stderr {stderr_without_trailing_newline}')


def main(playlist_id, videos_file_path):
    do_request = True
    video_list = read_file(videos_file_path)
    datetime_str = datetime.datetime.now().__str__().replace(":", "-").replace(' ', '_')
    log_file = open(os.path.join(os.path.abspath(os.sep), 'mnt', 'e', 'logs', f'yt_playlist_insert_{datetime_str}.log'),
                    'w')
    if do_request:
        youtube = get_youtube()

    def print_and_log(string, end='\n'):
        print(string, end=end)
        log_file.write(string + end)
        if end == '\n':
            log_file.flush()

    print_and_log(f'YOUTUBE_API_OAUTH: {os.environ["YOUTUBE_API_OAUTH"]}')
    print_and_log(f'Playlist URL: https://www.youtube.com/playlist?list={playlist_id}')
    print_and_log(f'Videos file path: {videos_file_path}')
    print_and_log(f'Log file path: {log_file.name}')

    if not do_request:
        print_and_log('\n!!! RUNNING IN DRY RUN !!!\n')

    ok_word = 'ok'
    if input(f'Type "{ok_word}" to continue: ') != ok_word:
        sys.exit(1)

    for i, line in enumerate(video_list):
        video_id_or_url = line[CSV_INDEX_URL]
        title = line[CSV_INDEX_TITLE]

        video_id = video_id_or_url.split('=')[-1]
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print_and_log(f'[{timestamp}] {i + 1}/{len(video_list)} {video_id} {title}', end=' ')

        try:
            if title in ['Deleted video', 'Private video']:
                raise Exception(title)

            test_unavailability(video_id)

            if do_request:
                request = create_request(youtube, playlist_id, video_id)
                request.execute()
                print_and_log('OK')
            else:
                print_and_log('OK DRY RUN')
        except Exception as e:
            print_and_log(f'\n\tError: {e}')

            next_keyword = "go"
            print(f'\nType {{{next_keyword}}} to go the next video.')
            while True:
                if input() == next_keyword:
                    break


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <playlist_id> <videos_file_path>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
