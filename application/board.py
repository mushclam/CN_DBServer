import functools
import json

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for
)
from .db import get_db

bp = Blueprint('board', __name__, url_prefix='/board')

@bp.route('/list')
def article():
    db = get_db()
    cursor = db.execute('SELECT * FROM article')
    rows = cursor.fetchall()
    result = []

    if rows is not None:
        for row in rows:
            id = row['id']
            type = row['type']
            title = row['title']
            author = row['author']
            time = row['time']
            list_item = {
                    'id':id,
                    'type':type,
                    'title':title,
                    'author':author,
                    'time':time
                    }
            result.append(list_item)

    return json.dumps(result, indent=2).encode('utf-8')

@bp.route('/article/<id>')
def show_article(id):
    db = get_db()
    row = db.execute(
            'SELECT * FROM article WHERE id = ?',
            (id,)
        ).fetchone()

    dir_row = {
            'id':row['id'],
            'title':row['title'],
            'author':row['author'],
            'time':row['time'],
            'body':row['body']
            }

    result = json.dumps(dir_row, indent=2).encode('utf-8')

    return result
