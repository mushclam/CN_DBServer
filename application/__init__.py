from contextlib import closing
import sqlite3
from flask import Flask, url_for, request, render_template, session, redirect, escape, g, flash, abort,\
        _app_ctx_stack
from crawl import crawl
import threading, time

app = Flask(__name__)
app.config.from_object(__name__)

def crawling():
    while True:
        crawl()
        time.sleep(60)
        print(msg)

if __name__ == '__main__':
    for msg in ['test']:
        t = threading.Thread(target=crawling, args=(msg,))
        t.daemon = True
        t.start()
