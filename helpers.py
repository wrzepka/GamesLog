import sqlite3
from flask import current_app, g

DB_NAME = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DB_NAME,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# Github copilot helped me here with: TypeError: close_db() takes 0 positional arguments but 1 was given.
# I just had to add 'useless' argument
def close_db(exception=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def has_uppercase(str):
    for char in str:
        if char.isupper():
            return True
    return False

def has_number(str):
    for char in str:
        if char.isdigit():
            return True
    return False

def has_special(str):
    if not str.isalnum():
        return True
    return False