import functools

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for
)
from .db import get_db

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/article')
def article():
    db = get_db()
    cursor = db.execute('SELECT * FROM article')
    rows = cursor.fetchall()
    result = ''

    if rows is not None:
        for row in rows:
            id = row['id']
            type = row['type']
            title = row['title']
            author = row['author']
            time = row['time']

            result += '<p><a href=' + url_for('test.article') + '/' + str(row['id']) + '>' \
                + str(row['id']) + ' ' + row[1] + ' ' + row[2] + ' ' + '</p>'

    return result

@bp.route('/article/<id>')
def show_article(id):
    db = get_db()
    row = db.execute(
            'SELECT * FROM article WHERE id = ?',
            (id,)
        ).fetchone()

    result = '<p>ID: ' + str(row['id']) + '</p>'
    result += '<p>Title: ' + row['title'] + '</p>'
    result += '<p>Author: ' + row['author'] + '</p>'
    result += '<p>Time: ' + row['time'] + '</p>'
    result += row['body']

    return result
