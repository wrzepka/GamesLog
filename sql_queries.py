import json

from db import get_db
from flask import session


# TODO: refactor app.py sql queries into functions here!

def get_user_playing_logs():
    db = get_db()

    games_sql = db.execute(
        "SELECT u.game_id, u.hours_played, u.rating, g.igdb_rating, g.name, g.img_id FROM users_logs u INNER JOIN games g ON g.id = u.game_id "
        "WHERE u.user_id = ? AND u.status = ?", (session['user_id'], "Playing")).fetchall()

    if len(games_sql) == 0:
        return []

    games_data = [dict(games) for games in games_sql]

    return games_data
