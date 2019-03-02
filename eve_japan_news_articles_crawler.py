import os
import os.path
import time
import urllib.error
import urllib.request

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

EVE_JAPAN_NEWS_PAGINATION = 10

#SITEURL = 'http://localhost:8000'
SITEURL = 'https://evekatsu.github.io/parrot-archives'

MARKDOWN = """Title: {title}
Date: {date}
Slug: {article_id}
Tags: {tags}

{text}
"""

def download_image(url, path):
    while True:
        try:
            data = urllib.request.urlopen(url).read()
            with open(path, mode="wb") as f:
                f.write(data)
            print('Download: ' + url)
            break
        except urllib.error.HTTPError:
            print('urllib.error.HTTPError: ' + url)
            time.sleep(60)
    time.sleep(2)

def main():
    base_url = 'https://eveonline-news.info/'
    driver = webdriver.Chrome()

    def generate_markdown(article_id):
        keywords = {'article_id': article_id}

        driver.get(base_url + str(article_id))
        WebDriverWait(driver, 60).until(lambda x: x.find_element_by_id('main'))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        article = soup.find('div', id='main').find('article')

        keywords['title'] = article.header.div.h1.string
        keywords['date'] = article.header.p.time['datetime']
        tag_elements = article.header.p.findAll('a', rel='tag')
        tag_list = []
        for tag_element in tag_elements:
            tag_list.append(tag_element.string)
        keywords['tags'] = ', '.join(tag_list)

        keywords['text'] = ''
        image_count = 1
        for p in article.section.findAll('p'):
            if p.get('class') == None or p.get('class')[0] == 'lead':
                for img in p.findAll('img'):
                    root, ext = os.path.splitext(img.get('src'))
                    img_path = '%d-%d%s' % (article_id, image_count, ext.split('?')[0].lower())
                    download_image(img.get('src'), os.path.join('content', 'images', img_path))
                    new_tag = soup.new_tag('img')
                    for key, value in img.attrs.items():
                        new_tag[key] = value

                    new_tag['src'] = SITEURL + '/images/' + img_path
                    new_tag['alt'] = '%s-%d' % (keywords['title'], image_count)
                    img.replace_with(new_tag)
                    image_count += 1
                keywords['text'] += str(p) + '\n'

        with open(os.path.join('content', 'translate', '%d.md' % article_id), 'w', encoding='utf-8') as file:
            file.write(MARKDOWN.format(**keywords))

    page_index = 1
    page_count = EVE_JAPAN_NEWS_PAGINATION

    while page_count == EVE_JAPAN_NEWS_PAGINATION:
        driver.get(base_url + ('category/translate/page/%d' % page_index))
        WebDriverWait(driver, 60).until(lambda x: x.find_element_by_id('main'))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        articles = soup.find('div', id='main').findAll('article')
        for article in articles:
            try:
                article_id = int(article.get('id').split('-')[1])
            except:
                break

            generate_markdown(article_id)
            time.sleep(2)

        page_index += 1
        page_count = len(articles)

if __name__ == '__main__':
    main()
