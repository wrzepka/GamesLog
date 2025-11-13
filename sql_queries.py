from db import get_db
from flask import session

def get_user_playing_logs(status_param: str):
    if status_param not in ["Wish", "Playing", "Finished"]:
        return []

    db = get_db()

    games_sql = db.execute(
        "SELECT u.game_id, u.hours_played, u.rating, g.igdb_rating, g.name, g.img_id FROM users_logs u INNER JOIN games g ON g.id = u.game_id "
        "WHERE u.user_id = ? AND u.status = ?", (session['user_id'], status_param)).fetchall()

    if len(games_sql) == 0:
        return []

    games_data = [dict(games) for games in games_sql]

    return games_data


def register_user(username, email, hashed_passwd):
    db = get_db()

    db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
               (username, email, hashed_passwd))
    db.commit()


def cache_games(data):
    # TODO: need to find solution for updating old games data (e.g. older than 7 days)
    db = get_db()

    for game in data:
        db.execute("INSERT INTO games (igdb_game_id, igdb_rating, name, img_id) "
                   "VALUES (?, ?, ?, ?)"
                   "ON CONFLICT(igdb_game_id) DO NOTHING;",
                   (game['id'], game['rating'], game['name'], game['img_id']))
    db.commit()


def get_cached_games(game_name):
    db = get_db()
    # TODO: Rewrite using upsert (maybe)
    games_json = db.execute("SELECT * from games WHERE name LIKE ? COLLATE NOCASE LIMIT ?",
                            (f'%{game_name}%', 30)).fetchall()

    return games_json


def is_game_in_user_logs(game_id, user_id):
    db = get_db()

    if db.execute("SELECT * from users_logs WHERE game_id = ? AND user_id = ?",(game_id, user_id)).fetchone():
        return True
    else:
        return False

def add_game_to_user_logs(game_id, type, user_id):
    db = get_db()

    db.execute(
        "INSERT INTO users_logs (user_id, game_id, status) VALUES (?, ?, ?);",
        (user_id, game_id, type),
    )
    db.commit()

def find_user(email):
    db = get_db()

    user = db.execute("SELECT * from users WHERE email = ?", (email,)).fetchone()

    return user

def get_user_name(user_id):
    db = get_db()

    username = db.execute("SELECT username from users WHERE id = ?", (user_id,)).fetchone()

    return username