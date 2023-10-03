from concurrent.futures import ThreadPoolExecutor

from lib.cda_parser import create_video_id, get_top_quality, get_video_data
from lib.utils import download_file, MAX_WORKERS
from lib.wbijam_parser import extract_all_episodes_links, extract_player_links

SAVE_PATH = "D:\\Download\\"
CATEGORY_URL = 'https://op.wbijam.pl/spec_tv.html'


def process_one_player_link(player_link):
    video_id = create_video_id(player_link)
    quality = get_top_quality(video_id)
    video_data = get_video_data(video_id, quality)
    download_file(video_data, SAVE_PATH, quality)


episodes_links = extract_all_episodes_links('ascending', CATEGORY_URL)
player_links = extract_player_links('cda', episodes_links)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    executor.map(process_one_player_link, player_links)


