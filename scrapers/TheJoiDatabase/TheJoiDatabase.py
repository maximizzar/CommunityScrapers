import os
import sys
import json

import requests
from dotenv import load_dotenv, dotenv_values
from bs4 import BeautifulSoup


def scrapeByURL():
    load_dotenv()
    #url: str = read_json_input().get('url')
    url: str = "https://www.the-joi-database.com/watch/04362c8e2096c22b7496d0f5"
    session = requests.Session()
    session.cookies.set("rt_token", os.getenv("rt_token"))
    session.cookies.set("token", os.getenv("token"))
    session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"})


def read_json_input() -> json:
    return json.loads(sys.stdin.read())


if __name__ == '__main__':
    if sys.argv[1] == "scrapeByURL":
        scrapeByURL()
