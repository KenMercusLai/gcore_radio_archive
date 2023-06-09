import os
import re
import sys
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

START_URL = 'https://www.gcores.com/radios'
MATCHING_PREFIX = '/radios'

SCRAPED_URLS = set()
SCRAPING_QUEUE = set()
EPISODE = namedtuple('Episode',
                     ['title', 'sub_title', 'hosts', 'publish_date', 'category', 'description', 'tags', 'likes',
                      'bookmarks', 'media', 'cover'])
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')


def index_scraper(start_url):
    # Use the 'requests' library to send a GET request to the website and save the response
    response = requests.get(start_url)

    # Check that the GET request had a 200 status code (meaning the request was successful)
    if response.status_code == 200:
        # Parse the response text with BeautifulSoup using a HTML parser
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all 'a' elements (links) in the HTML
        for link in soup.find_all('a'):
            href = link.get('href')
            # Check if the URL starts with the base URL
            if href and href.startswith(MATCHING_PREFIX):
                # print(href)
                if href not in SCRAPED_URLS:
                    SCRAPING_QUEUE.add(f'https://www.gcores.com{href}')


def extract_host_pic_name(node):
    return node.img['src'], node.find(class_='avatar_text').string


def episode_scraper(url: str) -> EPISODE:
    response = requests.get(url)

    # Check that the GET request had a 200 status code (meaning the request was successful)
    if response.status_code == 200:
        # Parse the response text with BeautifulSoup using an HTML parser
        soup = BeautifulSoup(response.text, 'html.parser')

        nodes = soup.find_all(class_='story_container')
        main_part = nodes[0]
        desc_tags_part = nodes[1]
        likes_bookmarks_part = nodes[2]

        title = main_part.find(class_='originalPage_title').text
        sub_title = main_part.find(class_='originalPage_desc').text
        hosts = list(map(extract_host_pic_name, main_part.find_all(class_='avatar')))
        publish_date = main_part.find(class_='me-2')['title']
        category = main_part.find(class_='u_color-category').text
        # print(title, sub_title, hosts, publish_date, category)

        description = list(map(lambda x: x.text, desc_tags_part.find_all(class_='story_block-text')))
        tags = list(map(lambda x: x.text, desc_tags_part.find_all(class_='is_tags')))
        # print(description, tags)

        likes = likes_bookmarks_part.find(class_='o_action_num').text
        bookmarks = likes_bookmarks_part.find(class_='o_bookmark_num').text
        # print(likes, bookmarks)

        media = soup.find(class_='ms-3')['href']
        cover_css = soup.find(class_='radioPage_header_mask')['style']
        jpg_url = re.findall(r'\((.*?)\)', cover_css)[0]
        cover = jpg_url.split('?')[0]
        # print(media, cover)
        return EPISODE(title, sub_title, hosts, publish_date, category, description, tags, likes, bookmarks, media,
                       cover)


def save_episode(episode: EPISODE):
    print(episode)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'all':
        first_page_only = False
    else:
        first_page_only = True

    # Start scraping from the following URL:
    SCRAPING_QUEUE.add(START_URL)
    while SCRAPING_QUEUE:
        url = SCRAPING_QUEUE.pop()
        if url in SCRAPED_URLS:
            continue
        SCRAPED_URLS.add(url)
        if re.match(r'https://www.gcores.com/radios/\d+', url):
            episode_info = episode_scraper(url)
            save_episode(episode_info)
        else:
            if first_page_only and url != START_URL:
                continue
            index_scraper(url)
