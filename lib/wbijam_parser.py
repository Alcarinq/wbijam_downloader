from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from lib.utils import MAX_WORKERS


def create_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}/"


def extract_all_episodes_links(order, category_url):
    print("Extracting all wbijam episodes links ...")
    episodes_links = []
    base_url = create_base_url(category_url)
    response = requests.get(category_url)

    # get all
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        for link in soup.find_all('a', href=True):
            if 'html' in link['href'] and '-' in link.attrs.get('href'):
                episodes_links.append(f"{base_url}{link['href']}")
    else:
        print("Error: ", response.status_code)

    if order == 'ascending':
        return episodes_links[::-1]
    else:
        return episodes_links


def process_one_player_link(player_link, player_name):
    response = requests.get(player_link)
    if response.status_code == 200:
        base_url = create_base_url(player_link)
        soup = BeautifulSoup(response.content, "html.parser")
        for content in soup.find_all('span', class_='odtwarzacz_link'):
            if player_name in content.parent.parent.text:
                return f"{base_url}odtwarzacz-{content['rel']}.html"
    else:
        print("Error: ", response.status_code)


def extract_player_links(player_name, episodes_links):
    print("Extracting all wbijam player links ... Depends on the number of episodes it could take a while ...")
    player_links = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for result in executor.map(process_one_player_link, episodes_links, repeat(player_name)):
            player_links.append(result)
    return player_links
