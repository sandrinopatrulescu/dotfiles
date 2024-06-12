#!/usr/bin/env python3
import datetime
import os
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def read_file(videos_file_path):
    lines = open(videos_file_path, 'r').read().splitlines()
    if len(lines) > 0 and lines[0].startswith('videoId'):
        lines.pop(0)
    return list(map(lambda line: line.split(','), lines))


def get_youtube():
    # Sample Python code for youtube.playlistItems.insert
    # See instructions for running these code samples locally:
    # https://developers.google.com/explorer-help/code-samples#python

    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = os.path.join(os.environ['DOTS_SECRETS'], os.environ['YOUTUBE_API_OAUTH'])

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()

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


def main(playlist_id, videos_file_path):
    do_request = True
    video_list = read_file(videos_file_path)
    datetime_str = datetime.datetime.now().__str__().replace(":", "-").replace(' ', '_')
    log_file = open(os.path.join(os.path.abspath(os.sep), 'mnt', 'e', 'logs', f'yt_playlist_insert_{datetime_str}.log'),
                    'w')
    if do_request:
        youtube = get_youtube()

    def print_and_log(string):
        print(string, end='')
        log_file.write(string)

    for i, [video_id, title, *_] in enumerate(video_list):
        prefix = f"{i + 1}/{len(video_list)} {video_id} {title} "
        print_and_log(prefix)

        if not do_request:
            print('OK DRY RUN')
            continue

        try:
            if title in ['Deleted video', 'Private video']:
                raise Exception(f'title is {title}')
            request = create_request(youtube, playlist_id, video_id)
            request.execute()
            print_and_log('OK\n')
        except Exception as e:
            print_and_log(f"Error: {e}\n")

            print('waiting for input=continue')
            while True:
                if input() == 'continue':
                    break


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
