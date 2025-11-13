from email.policy import default

from flask import Flask, render_template, request, redirect, session
from helpers import has_number, has_special, has_uppercase
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from wrapper import top10_games, find_games
from db import close_db
from sql_queries import get_user_playing_logs, register_user, cache_games, get_cached_games, is_game_in_user_logs, \
    add_game_to_user_logs, find_user, get_user_name

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET_KEY')
# After any request, close connection
app.teardown_appcontext(close_db)


@app.route('/')
def index():
    top_games_list = top10_games()

    return render_template('index.html', games=top_games_list)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        error = None
        email = request.form.get('email')
        password = request.form.get('password')

        if not email:
            error = 'email cannot be blank!'
        elif '@' not in email:
            error = 'email is wrong!'
        elif not password:
            error = 'password cannot be blank!'

        user = find_user(email)
        if not user or not check_password_hash(user['password'], password):
            error = 'invalid email or password'

        if error is not None:
            return render_template('login.html', error=error)
        else:
            session['user_id'] = user['id']
            username = get_user_name(user['id'])
            session['username'] = username['username']
            return redirect('/')
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        error = None
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        repassword = request.form.get('rePassword')
        password_len = len(password)

        if not username:
            error = 'username cannot be blank!'
        elif not email:
            error = 'email cannot be blank!'
        elif '@' not in email:
            error = 'email is wrong!'
        elif not password:
            error = 'password cannot be blank!'
        elif password_len > 20 or password_len < 8:
            error = 'password must be 8–20 characters long'
        elif not has_number(password) or not has_uppercase(password) or has_special(password):
            error = 'password must contain at least one uppercase letter and at least one number, and must not contain special characters or spaces.'
        elif not repassword:
            error = 'retyped password cannot be blank!'
        elif password != repassword:
            error = 'password does not match!'

        if error is not None:
            return render_template('register.html', error=error)
        else:
            hashed_passwd = generate_password_hash(password)
            register_user(username, email, hashed_passwd)

            return redirect('/')
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id')
    session.pop('username')
    return redirect('/')


@app.route('/profile')
def profile():
    playing = get_user_playing_logs("Playing")
    wishlisted = get_user_playing_logs("Wish")
    finished = get_user_playing_logs("Finished")
    return render_template('user_profile.html', playing=playing, wishlisted=wishlisted, finished=finished)


@app.route('/game/search', methods=['POST', 'GET'])
def game_search():
    if request.method == 'GET':
        return render_template('search_game.html')
    else:
        error = None
        game_name = request.form.get('game_name')

        if not game_name:
            error = "game name cannot be blank"
            return render_template('search_game.html', error=error)

        games_json = get_cached_games(game_name)

        if len(games_json) != 0:
            data = []

            for game in games_json:
                data.append({
                    'id': game['id'],
                    'name': game['name'],
                    'rating': game['igdb_rating'],
                    'img_id': game['img_id']
                })
        else:
            data = find_games(game_name)
            cache_games(data)

        return render_template('search_game.html', data=data, game_name=game_name)


@app.route('/game/<game_id>/status', methods=['POST'])
# TODO: Change name?
def add_game_to_logs(game_id):
    if not session['user_id']:
        return redirect('/login')

    type = request.form.get('type')

    if type == "Wish" or type == "Playing" or type == "Finished":
        if is_game_in_user_logs(game_id, session['user_id']):
            # TODO: Error handling?
            return redirect('/game/search')

        add_game_to_user_logs(game_id, type, session['user_id'])
    else:
        # TODO: Error handling?
        return redirect('/game/search')

    return redirect('/profile')
