import re

import requests
from bs4 import BeautifulSoup

START_URL = 'https://www.gcores.com/radios'
MATCHING_PREFIX = '/radios'

SCRAPED_URLS = set()
SCRAPING_QUEUE = set()


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
                print(href)
                SCRAPING_QUEUE.add(f'https://www.gcores.com{href}')


def extract_host_pic_name(node):
    return node.img['src'], node.find(class_='avatar_text').string


def episode_scraper(url):
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
        print(title, sub_title, hosts, publish_date, category)

        description = list(map(lambda x: x.text, desc_tags_part.find_all(class_='story_block-text')))
        tags = list(map(lambda x: x.text, desc_tags_part.find_all(class_='is_tags')))
        print(description, tags)

        likes = likes_bookmarks_part.find(class_='o_action_num').text
        bookmarks = likes_bookmarks_part.find(class_='o_bookmark_num').text
        print(likes, bookmarks)


if __name__ == '__main__':
    # Start scraping from the following URL:
    SCRAPING_QUEUE.add(START_URL)
    while SCRAPING_QUEUE:
        url = SCRAPING_QUEUE.pop()
        SCRAPED_URLS.add(url)
        if re.match(r'https://www.gcores.com/radios/\d+', url):
            episode_scraper(url)
            break
        else:
            index_scraper(url)
            print(len(SCRAPED_URLS), len(SCRAPING_QUEUE))
