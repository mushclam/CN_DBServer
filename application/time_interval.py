from crawl import crawl
import threading, time

def crawling():
    while True:
        print(time.ctime())
        crawl()
        time.sleep(10)

if __name__ == '__main__':
    crawling()
