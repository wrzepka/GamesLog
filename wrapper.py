import time
from igdb.wrapper import IGDBWrapper
import os
from dotenv import load_dotenv
import requests
import json

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
    platform_types = wrapper.api_request(
        'platform_types',
        # FIXME: Repair platform type (probably one more request for 'platform_type' endpoint)
        'fields *;'
    )

    platform_json = json.loads(platform_types.decode('utf-8'))

    games_bytes = wrapper.api_request(
        'games',
        # FIXME: Repair platform type (probably one more request for 'platform_type' endpoint!!!!!!!!)
        'fields id,name,total_rating, cover; sort total_rating desc; limit 10; where total_rating_count > 100;'
    )
    games_json = json.loads(games_bytes.decode('utf-8'))

    covers_id = [game['cover'] for game in games_json if 'cover' in game]
    covers_str = ','.join(str(i) for i in covers_id)
    covers_bytes = wrapper.api_request(
        'covers',
        f'fields image_id; where id = ({covers_str});'
    )

    covers_json = json.loads(covers_bytes.decode('utf-8'))
    covers_dict = {cover['id']: cover['image_id'] for cover in covers_json}
    result = []

    for game in games_json:
        img_id = covers_dict.get(game['cover'])
        result.append({
            'id': game['id'],
            'name': game['name'],
            'rating': round(game['total_rating'], 2),
            'img_id': img_id
        })

    return result


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
    data = []

    for game in games_json:
        rating = game.get('total_rating') if game.get('total_rating') is not None else None
        cover = game.get('cover') if game.get('cover') is not None else None

        img_id = None
        if cover is not None:
            img_id = cover.get('image_id')

        if rating is not None:
            rating = int(round(rating))

        data.append({
            'id': game['id'],
            'name': game['name'],
            'rating': rating,
            'img_id': img_id
        })

    return data
