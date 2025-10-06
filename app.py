from flask import Flask, render_template, request, redirect
from helpers import get_db, close_db, has_number, has_special, has_uppercase
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# After any request, close connection
app.teardown_appcontext(close_db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
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
