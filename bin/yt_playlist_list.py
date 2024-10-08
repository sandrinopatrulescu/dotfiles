#!/usr/bin/env python3
"""
program to run https://developers.google.com/youtube/v3/docs/playlistItems/list
"""
import json
import sys
from functools import reduce

from yt_playlist_insert import get_youtube


def main(playlist_id, file_name):
    youtube = get_youtube()
    responses = []
    is_first_request = True
    next_page_token_param_name = 'pageToken'
    request_params = {}
    call_number = 1

    while is_first_request or request_params.get(next_page_token_param_name) is not None:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=3000,
            playlistId=playlist_id,
            **request_params
        )
        response = request.execute()
        responses.append(response)
        request_params[next_page_token_param_name] = response.get('nextPageToken')
        print(f'{call_number}: {response["pageInfo"]} total={call_number * response["pageInfo"]["resultsPerPage"]}')
        call_number += 1
        is_first_request = False

    items = reduce(lambda acc, x: acc + x['items'], responses, [])

    # remove unneeded data
    for item in items:
        item['snippet'].pop('thumbnails', None)
        item['snippet'].pop('description', None)

    # save to file
    output_file = open(f'{file_name}.json', 'w')
    items_as_string = json.dumps(items, indent=4)
    output_file.write(items_as_string)
    print('Done!')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <playlist_id> <out basename root>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
