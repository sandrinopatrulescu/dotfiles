#!/usr/bin/env python3
import csv
import datetime
import json
import os.path
import sys
from typing import List, Tuple, Dict, Any

from yt_dlp import YoutubeDL

from yt_playlist_insert import get_youtube

"""
NOTE: ref := id/url
"""


def format_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


# load youtube client
youtube = get_youtube()
ydl_opts = {'quiet': True, 'no_warnings': True}
ydl = YoutubeDL(ydl_opts)
video_id_to_title: Dict[str, str] = {}

script_basename = os.path.basename(__file__)
basename_root = os.path.splitext(script_basename)[0]
log_file = open(os.path.join(os.getenv('LOGS'), f'{basename_root}_{format_datetime()}.log'), 'w')


def log(message: str):
    print(message)
    log_file.write(message + '\n')
    log_file.flush()


def ref_to_id(ref: str) -> str:
    return ref.split('=')[-1]


def search_existing_videos(list_file_path: str, video_ids: Dict[str, None]) -> Dict[str, Any]:
    # input: [LIST file path] [video id/url]
    # output: the json data of the video
    with open(list_file_path) as f:
        all_playlist_items = json.load(f)
        video_id_to_playlist_item = {key: None for key in video_ids}
        video_ids_set = video_ids.keys()

        for playlist_item in all_playlist_items:
            video_id = playlist_item['snippet']['resourceId']['videoId']
            if video_id in video_ids_set:
                video_id_to_playlist_item[video_id] = playlist_item

        return video_id_to_playlist_item


def replace_videos(playlist_id: str, tuple_list: List[Tuple[str, int, str, str]]):
    # add new video and remove old video
    # input: [playlist id/url] ([new video id/url] [position to insert] [old video playlist item id])

    for i, (new_video_id, position, old_video_playlist_item_id, name) in enumerate(tuple_list):
        log(f'DOING {i + 1}/{len(tuple_list)}: {new_video_id} {position} {old_video_playlist_item_id}: {name} -> {video_id_to_title[new_video_id]}')

        try:
            # add video
            request = youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "position": position,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": new_video_id
                        }
                    }
                }
            )
            request.execute()

            request = youtube.playlistItems().delete(id=old_video_playlist_item_id)
            request.execute()
        except Exception as e:
            log(f'Error: {e}')
            print(e)
            sys.exit(1)


def main(args: list[str]):
    # input: [playlist id/url] [LIST file path] [csv file with format: old video id/url,name,new video id/url]

    log('START')
    log(f'Using csv file {args[3]}')
    playlist_id = ref_to_id(args[1])
    csvreader = csv.reader(open(args[3]), delimiter=';')
    old_and_new_video_id_tuples = [(ref_to_id(row[0]), row[1], ref_to_id(row[2])) for row in csvreader]
    old_video_ids = {old_and_new_video_id_tuple[0]: None for old_and_new_video_id_tuple in old_and_new_video_id_tuples}
    old_video_id_to_playlist_item_dict = search_existing_videos(args[2], old_video_ids)

    for _, _, new_video_id in old_and_new_video_id_tuples:
        title = ydl.extract_info(f"https://www.youtube.com/watch?v={new_video_id}", download=False)['title']
        video_id_to_title[new_video_id] = title

    tuple_list = [(
        new_video_id,
        old_video_id_to_playlist_item_dict[old_video_id]['snippet']['position'],
        old_video_id_to_playlist_item_dict[old_video_id]['id'],
        name
    ) for old_video_id, name, new_video_id in old_and_new_video_id_tuples]

    log('The following videos will be replaced:')

    for i, (new_video_id, position, old_video_playlist_item_id, name) in enumerate(tuple_list):
        log(f'{i + 1}/{len(tuple_list)}: {new_video_id} {position} {old_video_playlist_item_id}: {name} -> {video_id_to_title[new_video_id]}')

    # prompt user for confirmation
    if input('Type "ok" to continue (otherwise operation is aborted): ') != 'ok':
        log('ABORT')
        sys.exit(1)

    replace_videos(playlist_id, tuple_list)
    log('END')
    print()


if __name__ == "__main__":
    main(sys.argv)
