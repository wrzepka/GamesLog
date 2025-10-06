from flask import Flask, render_template, request, redirect, session
from helpers import get_db, close_db, has_number, has_special, has_uppercase
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
# After any request, close connection
app.teardown_appcontext(close_db)


@app.route('/')
def index():
    return render_template('index.html')

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