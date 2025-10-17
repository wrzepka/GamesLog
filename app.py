from flask import Flask, render_template, request, redirect, session
from helpers import get_db, close_db, has_number, has_special, has_uppercase
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from wrapper import top10_games, search_games, get_games_img_id

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

        db = get_db()

        user = db.execute("SELECT * from users WHERE email = ?", (email, )).fetchone()
        if not user or not check_password_hash(user['password'], password):
            error = 'invalid email or password'

        if error is not None:
            return render_template('login.html', error=error)
        else:
            session['user_id'] = user['id']
            username = db.execute("SELECT username from users WHERE id = ?", (user['id'], )).fetchone()
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
            db = get_db()
            db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_passwd))
            db.commit()
            return redirect('/')
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route('/user_log')
def user_log():
    return render_template('user_logs.html')

@app.route('/game/search', methods=['POST', 'GET'])
def game_search():
    if request.method == 'GET':
        render_template('search_game.html')
    else:
        error = None
        game_name = request.form.get('game_name')

        if not game_name:
            error = "game name cannot be blank"
            render_template('user_logs.html', error=error)

        games_json = search_games(game_name)

        if len(games_json) == 0:
            render_template('user_logs.html', data=None)