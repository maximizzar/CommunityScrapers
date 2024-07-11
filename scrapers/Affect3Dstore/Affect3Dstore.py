import json
import syslog

import requests
import sys
import re
import base64

from bs4 import BeautifulSoup
from scrapers.py_common.types import ScrapedStudio, ScrapedScene, ScrapedTag


def read_json_input():
    return json.loads(sys.stdin.read())


# scape functions
def scrape_scene(soup: BeautifulSoup) -> ScrapedScene:
    # calls functions to get scene metadata

    return {
        "title": scrape_title(soup),
        "details": extract_details(soup),
        "url": url,
        "image": extract_image_url(soup),
        "studio": scrape_studio(soup),
        "tags": scrape_tags(soup),
    }


def scrape_studio(soup: BeautifulSoup) -> ScrapedStudio:
    # uses the Artists, because they created, but didn't Perform in the video

    product_attribute_table = extract_product_attribute_specs(soup)
    for row in product_attribute_table.find_all('tr'):
        th_elements = row.find_all('th')
        td_elements = row.find_all('td')

        for th, td in zip(th_elements, td_elements):
            if th.get_text() in ["Artist/Circle"]:
                studio: ScrapedStudio = {
                    "name": td.get_text(),
                    "url": td.get('href'),
                }
                if None not in [studio.get("name"), studio.get("url")]:
                    return studio

    artist_tag = soup.find(id='attr-artist-link')
    if artist_tag:
        return {
            "name": artist_tag.text.strip(),
            "url": artist_tag.get('href').strip(),
        }


def scrape_title(soup: BeautifulSoup) -> str:
    # try to get title from html body and falls back to head

    title = extract_page_title_wrapper(soup)
    if title is None:
        title = extract_meta_title(soup)
        if title is None:
            sys.exit("Title not found")
    return title


def scrape_tags(soup: BeautifulSoup) -> list[ScrapedTag]:
    # gets tags from body and head
    # merges them and returns a list of tags

    tags: list[ScrapedTag] = []
    product_attribute_table = extract_product_attribute_specs(soup)
    for row in product_attribute_table.find_all('tr'):
        th_elements = row.find_all('th')
        td_elements = row.find_all('td')

        for th, td in zip(th_elements, td_elements):
            if th.get_text() in ["Characters", "Content", "Breast Size", "Genre", "Language"]:
                for a in td.find_all('a'):
                    tags.append(ScrapedTag(name=a.get_text(strip=True)))

    meta_keywords = extract_meta_keywords(soup)
    if meta_keywords:
        for keyword in meta_keywords:
            if keyword not in tags:
                tags.append(keyword)
    return tags


# extract functions
def extract_page_title_wrapper(soup: BeautifulSoup) -> str | None:
    page_title_wrapper = soup.find('span', class_='base', itemprop='name')
    if page_title_wrapper:
        return page_title_wrapper.text


def extract_meta_title(soup: BeautifulSoup) -> str | None:
    # extracts the title from the title meta tog

    meta_title_tag = soup.find('meta', attrs={'name': 'title'})
    if meta_title_tag and 'content' in meta_title_tag.attrs:
        title_content = meta_title_tag['content']
        return title_content


def extract_meta_keywords(soup: BeautifulSoup) -> list[ScrapedTag] | None:
    # extracts tags from the keywords meta tag
    # is used as a fallback

    meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})

    if meta_keywords_tag and 'content' in meta_keywords_tag.attrs:
        keywords_content = meta_keywords_tag['content']
        keywords_array = [ScrapedTag(name=keyword.strip()) for keyword in keywords_content.split(',')]
        return keywords_array
    else:
        return None


def extract_product_attribute_specs(soup: BeautifulSoup) -> BeautifulSoup:
    product_attribute_specs = soup.find('table', id='product-attribute-specs-table')
    if product_attribute_specs not in [None, ""]:
        return product_attribute_specs
    sys.stderr.write("Failed to extract_product_attribute_specs!")
    sys.exit(1)


def extract_details(soup: BeautifulSoup) -> str:
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
        sys.stderr.write("Failed to extract_details!")
        sys.exit(1)


def extract_image_url(soup: BeautifulSoup) -> str:
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
        return json_dict.get('[data-gallery-role=gallery-placeholder]').get('mage/gallery/gallery').get('data')[0].get(
            'full')
    return sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1] == 'scrapeByURL':
        if sys.argv[2] == "Debug":
            url: str = {"url": "https://affect3dstore.com/elven-lust"}.get('url')
        else:
            url = read_json_input().get('url')

        cookies = requests.Session().cookies
        cookies.set("age-verify", "1")
        response = requests.get(url, cookies=cookies)

        beautifulSoup = BeautifulSoup(response.text, 'html.parser')

        if sys.argv[2] == "Debug":
            with open("scene.json", 'w') as file:
                file.write(json.dumps(scrape_scene(beautifulSoup)))
                file.close()
        else:
            print(json.dumps(scrape_scene(beautifulSoup)))
