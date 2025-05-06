import json
import sys
import subprocess
from typing import Dict, Any

from py_common.types import ScrapedImage, ScrapedStudio, ScrapedTag

def create_scraped_image(gdata: Dict[str, Any]) -> ScrapedImage | None:
    tags: list[ScrapedTag] = [ScrapedTag(name=t) for t in gdata["tags"]]

    if gdata['category'] == "pixiv":
        studio: ScrapedStudio = ScrapedStudio(
            name=gdata['user']['name'],
            url=f"https://www.pixiv.net/en/users/{gdata['user']['id']}",
        )

        return ScrapedImage(
            title=gdata['title'],
            code=gdata['id'],
            details=gdata['caption'],
            date=gdata['date'],
            studio=studio,
            tags=tags,
        )

        # TODO: pixiv impl
        print("pixiv")
    elif gdata['category'] == "fanbox":
        studio = ScrapedStudio(
            name=gdata["creatorId"],
            url=f"https://www.fanbox.cc/@{gdata['creatorId']}",
            image=gdata["user"]["iconUrl"]
        )

        return ScrapedImage(
            title=gdata["title"],
            code=gdata["id"],
            details=gdata["text"] if "None" not in str(gdata["text"]) else "",
            date=gdata["date"],
            studio=studio,
            tags=tags,
        )
    return None

def scrapeImageURL(url: str):
    gallery_dl = subprocess.run(
        ["gallery-dl", "--dump-json", url],
        capture_output=True,
        text=True,
        check=True,
    )

    try:
        json_data = json.loads(gallery_dl.stdout)
        scraped_image = create_scraped_image(json_data[0][1])
        print(scraped_image)

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)

def main():
    scrapeImageURL("https://www.fanbox.cc/@daisy-mitsumata/posts/9745153")
    scrapeImageURL("https://www.pixiv.net/en/artworks/127718177")


if __name__ == '__main__':
    main()
