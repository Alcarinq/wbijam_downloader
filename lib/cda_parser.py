import json
import time

import requests
from bs4 import BeautifulSoup
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent

from lib.utils import MAX_RETRIES, SLEEP_TIME


def generate_user_headers():
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()

    headers = {
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        'accept-language': 'pl-PL,pl;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        "User-Agent": user_agent,
    }

    return headers


def create_video_id(link):
    response = requests.get(link)
    if response.status_code != 200:
        print("Error:", response.status_code)
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for video in soup.find_all('a', href=True):
        if 'cda' in video['href']:
            return video['href'].split('/')[-1]


def get_top_quality_and_title(video_id):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        response = requests.get(f"https://www.cda.pl/video/{video_id}")
        if response.status_code == 200:
            data = response.text
            parser = BeautifulSoup(data, 'html.parser')
            player_data_elem = parser.find('div', {'player_data': True})
            if player_data_elem is None:
                print("player_data_elem is none:")
                return None

            player_data = json.loads(player_data_elem['player_data'])
            quality = list(player_data.get("video").get("qualities").keys())[-1]
            title = player_data['video']['title'].replace("kawa%C5%82ek", "one_piece")
            return quality, title
        elif response.status_code == 429:
            retry_after = response.headers["Retry-After"]
            print(f'Status code == {response.status_code} when downloading {video_id}, '
                  f'Retry-After == {retry_after} retrying after {retry_after}s ... (Attempt {retry_count}/{MAX_RETRIES})')
            retry_count += 1
            time.sleep(int(retry_after))
        else:
            print(f'Status code == {response.status_code} when downloading {video_id}, retrying... (Attempt {retry_count}/{MAX_RETRIES})')
            retry_count += 1
            time.sleep(SLEEP_TIME)


def get_video_file(video_id, quality):
    response = requests.get(f"https://ebd.cda.pl/1920x1080/{video_id}?wersja={quality}", headers=generate_user_headers())
    if response.status_code != 200:
        print("Error:", response.status_code)
        return None

    data = response.text
    parser = BeautifulSoup(data, 'html.parser')
    player_data_elem = parser.find('div', {'player_data': True})
    if player_data_elem is None:
        print("player_data_elem is none:")
        return None
    player_data = json.loads(player_data_elem['player_data'])

    return player_data['video']['file']
