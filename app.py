from flask import Flask, render_template, request, redirect
from helpers import close_db

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
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template('register.html')