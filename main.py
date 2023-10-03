import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from lib.cda_parser import create_video_id, get_top_quality, get_video_data
from lib.utils import download_file, MAX_WORKERS
from lib.wbijam_parser import extract_all_episodes_links, extract_player_links


def process_one_link(player_link, save_path):
    try:
        video_id = create_video_id(player_link)
        quality = get_top_quality(video_id)
        video_data = get_video_data(video_id, quality)
        download_file(video_data, save_path, quality)
    except FileNotFoundError as ex:
        print(ex)


def main():
    args = sys.argv
    if len(args) < 3:
        print("Usage: python main.py category_link save_link ...")
        print("Example: python main.py https://op.wbijam.pl/spec_ova.html D:\\Downloads\\")
        return

    category_url = args[1]
    save_path = args[2]

    episodes_links = extract_all_episodes_links('ascending', category_url)
    player_links = extract_player_links('cda', episodes_links)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(process_one_link, player_links, repeat(save_path))


if __name__ == "__main__":
    main()
