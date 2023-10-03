import sys
from datetime import time

import requests
from clint.textui import progress

from lib.cda_parser import decode_link

MAX_RETRIES = 5
SLEEP_TIME = 5
MAX_WORKERS = 6


def download_file(video_data, save_path, quality):
    download_link = f"https://{decode_link(video_data.get('video_file'))}.mp4"
    download_mp4(download_link, f"{save_path}{video_data.get('title')}.mp4", quality)


def retry_error(path, error_msg, retry_count):
    print(f'Error when downloading {path}: {error_msg}, retrying... (Attempt {retry_count}/{MAX_RETRIES})')
    retry_count += 1
    time.sleep(SLEEP_TIME)


def download_mp4(link, path, quality):
    retry_count = 0

    while retry_count < MAX_RETRIES:
        try:
            response = requests.get(link, stream=True)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    total_length = int(response.headers.get('content-length'))
                    print(f"Download started, URL: {link}, path: {path}, quality: {quality}, size: {total_length / 1024 / 1024:.2f} MB")
                    for chunk in progress.bar(response.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                print('File downloaded and saved in', path)
                return
            else:
                retry_error(path, response.status_code, retry_count)
        except requests.exceptions.RequestException as e:
            retry_error(path, str(e), retry_count)

    print(f'Failed to download the file {link} after {MAX_RETRIES} attempts.')
    print('File not downloaded.')
