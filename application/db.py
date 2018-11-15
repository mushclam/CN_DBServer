import sqlite3
from flask import current_app, g

def get_db():
    g.db = sqlite3.connect('notice.db')

    with current_app.open_resource('schema.sql') as f:
        g.db.executescript(f.read().decode('utf8')
