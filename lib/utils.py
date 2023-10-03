import os
import time

import requests
from clint.textui import progress
from lib.cda_parser import decode_link

MAX_RETRIES = 5
SLEEP_TIME = 5
MAX_WORKERS = 6


def download_file(video_data, file_path, quality):
    download_link = f"https://{decode_link(video_data.get('video_file'))}.mp4"
    download_mp4(download_link, file_path, quality)


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
                print(f'Status code == {response.status_code} when downloading {path}, retrying... (Attempt {retry_count}/{MAX_RETRIES})')
                retry_count += 1
                time.sleep(SLEEP_TIME)
        except requests.exceptions.RequestException as e:
            print(f'Exception occurs when downloading {path}: {str(e)}, retrying... (Attempt {retry_count}/{MAX_RETRIES})')
            retry_count += 1
            time.sleep(SLEEP_TIME)

    print(f'Failed to download the file {link} after {MAX_RETRIES} attempts.')
    print('File not downloaded.')


def check_if_file_exists(path):
    if os.path.exists(path):
        return True
    return False
