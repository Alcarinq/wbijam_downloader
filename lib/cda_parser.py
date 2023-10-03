import json
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'accept-language': 'pl-PL,pl;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 OPR/80.0.4170.63",
}


def create_video_id(link):
    response = requests.get(link)
    if response.status_code != 200:
        print("Error:", response.status_code)
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for video in soup.find_all('a', href=True):
        if 'cda' in video['href']:
            return video['href'].split('/')[-1]


def get_top_quality(video_id):
    response = requests.get(f"https://www.cda.pl/video/{video_id}")
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
    quality = list(player_data.get("video").get("qualities").keys())[-1]
    return quality


def get_video_data(video_id, quality):
    response = requests.get(f"https://ebd.cda.pl/1920x1080/{video_id}?wersja={quality}", headers=HEADERS)
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

    return {
        'video_file': player_data['video']['file'],
        'title': player_data['video']['title'].replace("kawa%C5%82ek", "one_piece")
    }


def decode_link(link):
    quotes = ["_XDDD", "_CDA", "_ADC", "_CXD", "_QWE", "_Q5", "_IKSDE"]

    for e in quotes:
        link = unquote(link.replace(e, ""))

    b = []
    for i in range(len(link)):
        f = ord(link[i])
        if 33 <= f <= 126:
            b.append(chr(33 + ((f + 14) % 94)))
        else:
            b.append(chr(f))

    link = ''.join(b)
    link = link.replace(".cda.mp4", "")
    link = link.replace(".2cda.pl", ".cda.pl")
    link = link.replace(".3cda.pl", ".cda.pl")

    return link
