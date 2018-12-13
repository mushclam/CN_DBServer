import sqlite3
import requests, json
import yaml
from bs4 import BeautifulSoup
import getpass
import threading
from datetime import datetime
import time
import os

from flask import current_app, g
from flask.cli import with_appcontext
from .db import get_db

def crawl():
    # connect with database
    # conn = sqlite3.connect('crawl.db')
    conn = get_db()
    # if article table is not exist, create table
    # found last updated time
    cursor = conn.execute('SELECT time FROM article ORDER BY time DESC')
    row = cursor.fetchone()
    if row != None:
        last_update = row[0]
    else :
        last_update = ''

    # Read login config file
    with open(current_app.config['CONFIG'], 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    user_id = cfg['user_id']
    #user_id = input('ID: ')
    password = cfg['password']
    #password = getpass.getpass('Password: ')
    keep_signed = cfg['keep_signed']

    # Login to college site
    url = 'https://college.gist.ac.kr/main/index.php'
    r_url = 'https://college.gist.ac.kr/main/index.php?act=dispMemberLoginForm'
    params = { 'act' : 'procMemberLogin' }
    headers = { 'Content-Type' : 'application/x-www-form-urlencoded', 'Referer' : r_url }
    data = {'user_id' : user_id, 'password' : password, 'keep_signed' : keep_signed }

    session = requests.Session()
    res = session.post(url=url, headers=headers, data=data, params=params)
    status = res.status_code
    cookies = session.cookies.get_dict()

    flag = False
    # if logged in successfully, load board content
    if status == 200:

        #end_page = int(input("page: ")) + 1
        end_page = 10 + 1

        print('[Crawling Start]')
        for page in range(1,end_page):
            # Move to board page
            b_params = { 'mid' : 'Sub040203', 'page' : str(page) }
            b_res = session.get(url=url, params=b_params, cookies=cookies)
            b_status = b_res.status_code
            _html = b_res.text

            # if load board successfully, inquiry each article in board
            if b_status == 200:
                soup = BeautifulSoup(_html, 'html.parser')
                board_area = soup.find("div", {"class":"board_list"}).find("table").find("tbody").find_all("tr")

                for article in board_area:

                    # if in page 1, save notice article and check type notice
                    # if not in page 1, ignore notice article
                    if page == 1 and article.has_attr('class'):
                        a_type = 'notice'
                    elif page != 1 and article.has_attr('class'):
                        continue
                    else:
                        a_type = 'normal'

                    item = article.find("td", {"class":"title"}).find("a")
                    _link = item['href']

                    a_res = requests.get(url=_link, cookies=cookies)
                    a_html = a_res.text
                    a_status = a_res.status_code
        
                    if a_status == 200:
                        a_soup = BeautifulSoup(a_html, 'html.parser')
                        article_area = a_soup.find("div", {"class":"board_read"})
            
                        header_area = article_area.find("div", {"class":"read_header"})
                        body_area = article_area.find("div", {"class":"read_body"})

                        a_title = header_area.find("h1").find("a").text.strip()
                        a_meta = header_area.find("p", {"class":"meta"})
                        a_author = a_meta.find("span", {"class":"author"}).find("a").text.strip()
                        a_time = a_meta.find("span", {"class":"time"}).text.strip()
                        a_count = a_meta.find("span", {"class":"read_count"}).text.strip()
                        a_body = str(body_area)

                        # if timestamp of last article on site is same or smaller than last timestamp of db
                        # then not download data of website
                        if (a_time <= last_update):
                            print('[Already Lastest State: ' + last_update + ']')
                            flag = True
                            break

                        """
                        dup = conn.execute('SELECT title FROM article WHERE time = ?',
                                (a_time,)
                            ).fetchone()
                        if dup is not None:
                            print('[Duplicated]')
                            return
                        """
                        
                        conn.execute('''
                            INSERT INTO article (type, title, author, time, body)
                            VALUES (?, ?, ?, ?, ?)
                            ''',
                            (a_type, a_title, a_author, a_time, a_body)
                        )
                        conn.commit()

            if flag:
                break
            print('Crawling for page [' + str(page) + '] is Completed!')
    if flag == False:
        print('Crawling is Done!')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    crawl()
