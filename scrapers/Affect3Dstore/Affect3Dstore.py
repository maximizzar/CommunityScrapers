import json
from typing import List

import requests
import sys
import re

from bs4 import BeautifulSoup
from scrapers.py_common.types import ScrapedStudio, ScrapedScene


def read_json_Input():
    return json.loads(sys.stdin.read())


# scape functions
def scrape_scene(soup: BeautifulSoup) -> ScrapedScene:
    title = extract_meta_title(soup)
    details = extract_details(soup)
    image = ""


def scrape_studio(soup: BeautifulSoup) -> ScrapedStudio:
    artist_tag = soup.find(id='attr-artist-link')
    if artist_tag:
        return {
            "name": artist_tag.text.strip(),
            "url": artist_tag.get('href').strip(),
        }


# extract functions
def extract_meta_title(soup: BeautifulSoup) -> str | None:
    # Find the <meta> tag with name="title"
    meta_title_tag = soup.find('meta', attrs={'name': 'title'})

    if meta_title_tag and 'content' in meta_title_tag.attrs:
        title_content = meta_title_tag['content']
        return title_content
    else:
        return None


def extract_meta_keywords(soup: BeautifulSoup) -> list[str] | None:
    # Find the <meta> tag with name="keywords"
    meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})

    if meta_keywords_tag and 'content' in meta_keywords_tag.attrs:
        keywords_content = meta_keywords_tag['content']
        keywords_array = [keyword.strip() for keyword in keywords_content.split(',')]
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


def extract_image_url(soup: BeautifulSoup) -> list[str] | None:
    pattern = r'\[data-gallery-role=gallery-placeholder\]'
    script_tags = soup.find_all('script', type='text/x-magento-init')

    for script_tag in script_tags:
        match = re.search(pattern, script_tag.text)
        if not match:
            continue
        array_data = re.search(pattern, script_tag.text)
        if array_data:
            array_values = array_data.group(1)
            array_in_python = eval("[" + array_values + "]")  # Using eval to parse mixed data types
            return array_in_python
    return None


def save_image_from_url(iurl, save_path):
    response = requests.get(iurl)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved successfully to {save_path}")
    else:
        print("Failed to download the image")


if __name__ == "__main__":
    url = "https://affect3dstore.com/corporate-training-2"
    response = requests.get(url)
    beautifulSoup = BeautifulSoup(response.text, 'html.parser')

    print(extract_image_url(beautifulSoup))

# data-gallery-role=gallery-placeholder
    # data json-object
