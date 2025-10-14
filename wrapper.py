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

# TO FIX XD
# def validate_token(auth_date, token):
#     expiration_time = token['expires_in']
#     if time.time() > auth_date + expiration_time - 60:
#         return False
#     return True


ACCESS_TOKEN = get_token()
auth_time = time.time()

wrapper = IGDBWrapper(IGDB_CLIENT, ACCESS_TOKEN['access_token'])


def top10_games():
    games_bytes = wrapper.api_request(
        'games',
        # TODO: Repair platform type (probably one more request for 'platform_type' endpoint)
        'fields name,total_rating, cover; sort total_rating desc; limit 10; where total_rating_count > 100;'
    )
    games_json = json.loads(games_bytes.decode('utf-8'))

    covers_id = [game['cover'] for game in games_json if 'cover' in game]
    covers_str = ','.join(str(i) for i in covers_id)
    covers_bytes = wrapper.api_request(
        'covers',
        f'fields image_id; where id = ({covers_str});'
    )

    covers_json = json.loads(covers_bytes.decode('utf-8'))
    covers_dict = {cover['id'] : cover['image_id'] for cover in covers_json}
    result = []

    for game in games_json:
        img_id = covers_dict.get(game['cover'])
        result.append({
            'name':game['name'],
            'rating':round(game['total_rating'], 2),
            'url':f"https://images.igdb.com/igdb/image/upload/t_logo_med_2x/{img_id}.jpg"
        })

    return result