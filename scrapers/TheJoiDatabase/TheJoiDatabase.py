import datetime
import os
import sys
import json

import requests
from dotenv import load_dotenv, dotenv_values
from bs4 import BeautifulSoup

from scrapers.py_common.types import \
    ScrapedPerformer, ScrapedStudio, ScrapedMovie, ScrapedGallery, ScrapedScene, ScrapedTag, \
    SceneSearchResult


def search_scene(soup: BeautifulSoup) -> SceneSearchResult | None:
    scene: SceneSearchResult = {}

    title = get_title(soup)
    if not title:
        return None
    scene['title'] = title

    url = get_url(soup)
    if not url:
        return None
    scene['url'] = url

    date = get_date(soup)
    if date:
        scene['date'] = date

    image = get_scene_image_url(soup)
    if image:
        scene['image'] = image

    tags = get_tags(soup)
    if tags:
        scene['tags'] = tags

    performers = scrape_performers(soup)
    if performers:
        scene['performers'] = performers

    if uploader_as_studio:
        studio = scrape_studio(soup)
        if studio:
            scene['studio'] = studio
    return scene


def scrape_performers(soup: BeautifulSoup) -> list[ScrapedPerformer] | None:
    return None


def scrape_studio(soup: BeautifulSoup) -> ScrapedStudio | None:
    # soup object needs to be initialized with profile url (/profile)
    studio: ScrapedStudio = {}

    name = get_title(soup)
    if name:
        studio['name'] = name
    else:
        return None

    url = get_url(soup)
    if url:
        studio['url'] = url

    if create_parent_studio:
        studio['parent']: ScrapedStudio = {
            "name": "The joi Database",
            "url": "https://www.the-joi-database.com/",
        }

    image = get_studio_image_url(soup)
    if image:
        studio['image'] = image
    return studio


def scrape_movies(soup: BeautifulSoup) -> list[ScrapedMovie] | None:
    return None


def scrape_gallery(soup: BeautifulSoup) -> ScrapedGallery | None:
    return None


def scrape_scene(soup: BeautifulSoup) -> ScrapedScene | None:
    # soup object needs to be initialized with video url (/watch)
    scene_data: ScrapedScene = {}

    title = get_title(soup)
    if title:
        scene_data['title'] = title

    details = get_details(soup)
    if details:
        scene_data['details'] = details

    url = get_url(soup)
    if url:
        scene_data['url'] = url

    date = get_date(soup)
    if date:
        scene_data['date'] = date

    image = get_scene_image_url(soup)
    if image:
        scene_data['image'] = image

    movies: list[ScrapedMovie] = scrape_movies(soup)
    if movies:
        scene_data['movies'] = movies

    if uploader_as_studio:
        studio_soup = get_studio_soup(soup)
        if studio_soup:
            studio = scrape_studio(studio_soup)
            if studio:
                scene_data['studio'] = studio

    performers: list[ScrapedPerformer] = scrape_performers(soup)
    if performers:
        scene_data['performers'] = performers

    code = get_code(soup)
    if code:
        scene_data['code'] = code

    tags = get_tags(soup)
    if tags:
        scene_data['tags'] = tags

    if scene_data:
        return scene_data
    return None


def get_title(soup: BeautifulSoup) -> str | None:
    html_tag = soup.find('meta', attrs={'name': 'title'})
    if html_tag:
        return html_tag.get('content').strip()
    return None


def get_details(soup: BeautifulSoup) -> str | None:
    html_tag = soup.find('p', attrs={'class': 'my-0'})
    if html_tag:
        return html_tag.text.strip()
    return None


def get_url(soup: BeautifulSoup) -> str | None:
    html_tag = soup.find('meta', attrs={'name': 'url'})
    if html_tag:
        return html_tag.get('content').strip()
    return None


def get_date(soup: BeautifulSoup) -> str | None:
    # soup object needs to be initialized with video url (/watch)

    html_tag = soup.find('small', attrs={'class': 'text-muted'})
    if html_tag:
        text_content = html_tag.get_text()
        date_string = text_content.split('•')[-1].strip()
        date_object = datetime.datetime.strptime(date_string, '%b %d, %Y')
        return date_object.strftime('%Y-%m-%d')
    return None


def get_scene_image_url(soup: BeautifulSoup) -> str | None:
    html_tag = soup.find('meta', attrs={'property': 'og:image'})
    if html_tag:
        return html_tag.get('content').strip()
    return None


def get_studio_image_url(soup: BeautifulSoup) -> str | None:
    html_tag = soup.find('img', attrs={'class': 'profile-image-100 mr-2 mr-md-3'})
    if html_tag:
        return html_tag.get('src').strip()
    return None


def get_tags(soup: BeautifulSoup) -> list[ScrapedTag] | None:
    # soup object needs to be initialized with video url (/watch)

    html_tags = soup.find('div', attrs={'id': 'tags'}).find_all('a')
    if html_tags:
        list_of_tags: list[ScrapedTag] = []
        for html_tag in html_tags:
            list_of_tags.append(ScrapedTag(name=html_tag.text.strip()))
        return list_of_tags
    return None


def get_code(soup: BeautifulSoup) -> str | None:
    # soup object needs to be initialized with video url (/watch)

    html_tag = soup.find('a', attrs={'class': 'video-title'})
    if html_tag:
        return html_tag.get('href').strip()[len("/watch/"):]


def sceneByName() -> SceneSearchResult:
    # wip
    load_dotenv()
    url: str = "https://www.the-joi-database.com/videos?search={}" + read_json_input().get('name')
    url.replace(" ", "+")

    # set cookies and headers
    session = requests.Session()
    session.cookies.set("rt_token", os.getenv("rt_token"))
    session.cookies.set("token", os.getenv("token"))

    response = requests.get(url)
    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    scraped_data = search_scene(soup)
    if scraped_data:
        return scraped_data
    sys.stderr.write(f"Could not find a video under {url}\n")
    sys.exit(1)


def sceneByURL() -> ScrapedScene:
    load_dotenv()

    #url: str = read_json_input().get('url')
    url: str = {"url": "https://www.the-joi-database.com/watch/fb22cad92271b457d495a3db"}.get('url')

    session = create_session()
    response = session.get(url)
    if response.headers.get('rt_token') not in ["", None]:
        update_token(os.getenv("rt_token"), response.headers.get('rt_token'), 'rt_token')
    if response.headers.get('token') not in ["", None]:
        update_token(os.getenv("token"), response.headers.get('token'), 'token')
    load_dotenv()

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

    scraped_data = scrape_scene(soup)
    if scraped_data:
        return scraped_data
    sys.stderr.write(f"Could not scrape {url}\n")
    sys.exit(1)


# helper
def get_studio_soup(soup: BeautifulSoup) -> BeautifulSoup | None:
    studio_sub_path = soup.find('a', attrs={'class': 'd-block mr-2 mr-md-3'}).get('href').strip()
    studio_url = "https://www.the-joi-database.com" + studio_sub_path.strip()

    session = create_session()
    return BeautifulSoup(session.get(studio_url).text, 'html.parser')


def read_json_input():
    return json.loads(sys.stdin.read())


def update_token(old_token: str, new_token: str, token_name: str) -> None:
    if old_token == new_token:
        return None
    if len(old_token) is not len(new_token):
        sys.stderr.write(f"{token_name} does not have the same length as it's predecessor\n")
        sys.exit(1)

    env_file_path = '.env'

    with open(env_file_path, 'r') as file:
        lines = file.readlines()

    with open(env_file_path, 'w') as file:
        for line in lines:
            if line.startswith(f'{token_name}='):
                file.write(f'{token_name}={new_token}\n')
            else:
                file.write(line)


def create_session() -> requests.Session:
    session: requests.Session = requests.Session()
    if os.getenv("rt_token") not in ["", None]:
        session.cookies.set("rt_token", os.getenv("rt_token"))
    if os.getenv("token") not in ["", None]:
        session.cookies.set("token", os.getenv("token"))
    session.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"})
    session.headers.update({"Accept-Encoding": "gzip, deflate"})
    session.headers.update({"Accept-Language": "en-US,en;q=0.8"})
    return session


# global flags (edit to your liking)
uploader_as_studio = True
create_parent_studio = True

# main
if __name__ == '__main__':
    if sys.argv[1] == "scrapeByURL":
        print(json.dumps(sceneByURL()))
