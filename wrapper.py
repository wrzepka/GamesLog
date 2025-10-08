import time
from igdb.wrapper import IGDBWrapper
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
CLIENT_ID = os.getenv("IGDB_CLIENT")
SECRET_KEY = os.getenv("IGDB_SECRET")


def get_token():
    url = "https://id.twitch.tv/oauth2/token"
    request = requests.post(url, data={
        'client_id': CLIENT_ID,
        'client_secret': SECRET_KEY,
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

wrapper = IGDBWrapper(CLIENT_ID, "Bearer " + ACCESS_TOKEN['access_token'])


def top10_games():
    games_bytes = wrapper.api_request(
        'games',
        'fields name,rating, cover; sort rating desc; limit 10;'
    )
    games_json = json.loads(games_bytes.decode('utf-8'))
    covers_id = [game['cover'] for game in games_json if 'cover' in game]
    covers_str = ','.join(str(i) for i in covers_id)

    covers_bytes = wrapper.api_request(
        'cover',
        f'fields image_id; where id = ({covers_str})'
    )

    cover_json = json.loads(covers_bytes.decode('utf-8'))

    "https://images.igdb.com/igdb/image/upload/t_logo_med/{}.jpg"

    result = []

    for game, cover in games_json, cover_json:
        result.append({
            'name':game['name'],
            'rating':game['rating'],
            'url':f"https://images.igdb.com/igdb/image/upload/t_logo_med/{cover['image_id']}.jpg"
        })

    return result