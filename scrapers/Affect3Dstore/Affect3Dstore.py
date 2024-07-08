import json
from typing import List

import requests
import sys
import re
import base64

from bs4 import BeautifulSoup
from scrapers.py_common.types import ScrapedStudio, ScrapedScene, ScrapedTag


def read_json_Input():
    return json.loads(sys.stdin.read())


# scape functions
def scrape_scene(soup: BeautifulSoup) -> ScrapedScene:
    return {
        "title": extract_meta_title(soup),
        "details": extract_details(soup),
        "url": url,
        "image": download_image(soup),
        "studio": scrape_studio(soup),
        "tags": scrape_tags(soup),
    }


def scrape_studio(soup: BeautifulSoup) -> ScrapedStudio:
    artist_tag = soup.find(id='attr-artist-link')
    if artist_tag:
        return {
            "name": artist_tag.text.strip(),
            "url": artist_tag.get('href').strip(),
        }


def scrape_tags(soup: BeautifulSoup) -> list[ScrapedTag]:
    return extract_meta_keywords(soup)


# extract functions
def extract_meta_title(soup: BeautifulSoup) -> str | None:
    # Find the <meta> tag with name="title"
    meta_title_tag = soup.find('meta', attrs={'name': 'title'})

    if meta_title_tag and 'content' in meta_title_tag.attrs:
        title_content = meta_title_tag['content']
        return title_content
    else:
        return None


def extract_meta_keywords(soup: BeautifulSoup) -> list[ScrapedTag] | None:
    # Find the <meta> tag with name="keywords"
    meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})

    if meta_keywords_tag and 'content' in meta_keywords_tag.attrs:
        keywords_content = meta_keywords_tag['content']
        keywords_array = [ScrapedTag(name=keyword.strip()) for keyword in keywords_content.split(',')]
        #keywords_array: list[str] = [keyword.strip() for keyword in keywords_content.split(',')]
        return keywords_array
    else:
        return None


def extract_details(soup: BeautifulSoup) -> str | None:
    # Find the <div> tag with class value and itemprop="description"
    description_div = soup.find('div', class_='value', itemprop='description')

    if description_div:
        description_text = ''

        for element in description_div.children:
            if element.name == 'h3':
                break
            if hasattr(element, 'text'):
                description_text += element.text.strip() + ' '

        return description_text.strip()
    else:
        return None


def extract_description_from_h2(soup: BeautifulSoup) -> str | None:
    h2_tag = soup.find('h2', class_='page-custom-description')
    if h2_tag:
        return h2_tag.text
    else:
        return None


def extract_image_url(soup: BeautifulSoup) -> str | None:
    pattern = r'\[data-gallery-role=gallery-placeholder\]'
    script_tags = soup.find_all('script', type='text/x-magento-init')

    for script_tag in script_tags:
        match = re.search(pattern, script_tag.text)
        if not match:
            continue

        json_start = script_tag.text.find('{')
        json_end = script_tag.text.rfind('}') + 1
        json_object = script_tag.text[json_start:json_end]
        json_dict = json.loads(json_object)
        return json_dict.get('[data-gallery-role=gallery-placeholder]').get('mage/gallery/gallery').get('data')[0].get('full')
    return None


def download_image(soup: BeautifulSoup) -> str | None:
    image_url = extract_image_url(soup)
    image_res = requests.get(image_url)

    if image_res.status_code == 200:
        # Convert the image content to base64
        image_base64 = base64.b64encode(image_res.content)

        # Convert bytes to string
        return image_base64.decode('utf-8')
    return None

def read_json_input():
    json_input = sys.stdin.read()
    return json.loads(json_input)

if __name__ == "__main__":
    if sys.argv[1] == 'scrapeByURL':
        url = read_json_input().get('url')
        response = requests.get(url)
        beautifulSoup = BeautifulSoup(response.text, 'html.parser')
        print(json.dumps(scrape_scene(beautifulSoup)))
