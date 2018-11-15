import sqlite3
import requests, json, yaml
from bs4 import BeautifulSoup

def crawl():
    conn = sqlite3.connect('crawl.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS article (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            time TEXT NOT NULL,
            content TEXT);'''
    )

    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    user_id = cfg['user_id']
    password = cfg['password']
    keep_signed = cfg['keep_signed']

    url = 'https://college.gist.ac.kr/main/index.php?mid=Sub040203&act=procMemberLogin'
    r_url = 'https://college.gist.ac.kr/main/?mid=Sub040203&act=dispMemberLoginForm'
    headers = { 'Content-Type' : 'application/x-www-form-urlencoded', 'Referer' : r_url }
    params = {'user_id' : user_id, 'password' : password, 'keep_signed' : keep_signed }

    session = requests.Session()
    res = session.post(url=url, headers=headers, data=params)

    _html = res.text
    status = res.status_code
    cookies = session.cookies.get_dict()

    if status == 200:
        soup = BeautifulSoup(_html, 'html.parser')
        board_area = soup.find("div", {"class":"board_list"}).find("table").find("tbody").find_all("tr")
        i = 0
        for article in board_area:
            #if article.has_attr('class'):
                #print("[Notice]", end=" ")
            item = article.find("td", {"class":"title"}).find("a")
            _link = item['href']

            a_res = requests.get(url=_link, cookies=cookies)

            a_html = a_res.text
            a_status = a_res.status_code
        
            if a_status == 200:
                a_soup = BeautifulSoup(a_html, 'html.parser')
                article_area = a_soup.find("div", {"class":"board_read"})
            
                header_area = article_area.find("div", {"class":"read_header"})
                a_title = header_area.find("h1").find("a").text.strip()
                a_meta = header_area.find("p", {"class":"meta"})
                a_author = a_meta.find("span", {"class":"author"}).find("a").text.strip()
                a_time = a_meta.find("span", {"class":"time"}).text.strip()
                a_count = a_meta.find("span", {"class":"read_count"}).text.strip()
            
                conn.execute('''
                    INSERT INTO article (title, author, time)
                    VALUES (?, ?, ?)
                    ''',
                    (a_title, a_author, a_time)
                )
                conn.commit()
    cursor = conn.execute("SELECT * FROM article")
    for row in cursor:
        print("ID: " + str(row[0]))
        print("Title: " + row[1])
        print("Author: " + row[2])
        print("Time: " + row[3])

    conn.execute("DELETE FROM article")
    conn.commit()

    conn.close()

crawl()
