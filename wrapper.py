import time
from igdb.wrapper import IGDBWrapper
import os
from dotenv import load_dotenv
import requests
import json

from helpers import summarize_games

load_dotenv()
IGDB_CLIENT = os.getenv("IGDB_CLIENT")
IGDB_SECRET = os.getenv("IGDB_SECRET")


def get_token():
    url = "https://id.twitch.tv/oauth2/token"
    request = requests.post(url, data={
        'client_id': IGDB_CLIENT,
        'client_secret': IGDB_SECRET,
        'grant_type': 'client_credentials'
    })
    request.raise_for_status()
    return request.json()


ACCESS_TOKEN = get_token()
auth_time = time.time()

wrapper = IGDBWrapper(IGDB_CLIENT, ACCESS_TOKEN['access_token'])


# Only for testing purposes. To delete.
def top10_games():
    # TODO: In future expand that (return more data)
    games_bytes = wrapper.api_request(
        'games',
        f'fields id, name, total_rating, cover.image_id;'
        f' where platforms.name = ("PC (Microsoft Windows)", "Mac", "Xbox Series X|S", "PlayStation 5", "Xbox One", "Playstation 4", "Xbox 360", "Playstation 3")'
        f'& game_type.type != "Mod" & total_rating_count > 500;'
        f'sort rating desc;'
        f'limit 50;'
    )

    games_json = json.loads(games_bytes.decode('utf-8'))
    data = summarize_games(games_json)

    return data


def find_games(name):
    # TODO: In future expand that (return more data)
    games_bytes = wrapper.api_request(
        'games',
        f'fields id, name, total_rating, cover.image_id;'
        f' search "{name}";'
        f' where platforms.name = ("PC (Microsoft Windows)", "Mac", "Xbox Series X|S", "PlayStation 5", "Xbox One", "Playstation 4", "Xbox 360", "Playstation 3")'
        f'& game_type.type != "Mod";'
    )

    games_json = json.loads(games_bytes.decode('utf-8'))
    data = summarize_games(games_json)

    return data
