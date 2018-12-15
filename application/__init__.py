import os
import sqlite3
import threading
import atexit

from flask import (
        Flask, url_for, request, render_template, session, redirect, escape, g, flash, abort,_app_ctx_stack
    )
from flask_restful import Resource, Api, reqparse

POOL_TIME = 60

dataLock = threading.Lock()
thread = threading.Thread()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        CONFIG=os.path.join(app.instance_path, 'config.yml')
    )
    api = Api(app)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    class CreateUser(Resource):
        def post(self):
            return {'status':'success'}

    from . import db
    db.init_app(app)
    
    from . import board
    app.register_blueprint(board.bp)

    from . import crawl
    def interrupt():
        global thread
        thread.cancel()

    def loopCrawl():
        global thread
        with dataLock:
            with app.app_context():
                crawl.crawl()
        thread = threading.Timer(POOL_TIME, loopCrawl, ())
        thread.start()

    loopCrawl()
    atexit.register(interrupt)

    api.add_resource(CreateUser, '/user')

    return app
