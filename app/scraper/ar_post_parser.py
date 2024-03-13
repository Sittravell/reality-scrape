from __future__ import annotations
from bs4 import BeautifulSoup
import requests
import time
import traceback
from .parse_exceptions import ListLinkConnectionError, ParseListError, ParseNextUrlError, ParseContentError, ParseImageError, PostLinkConnectionError
from datetime import datetime
import sys
class ARPostParser():
    LINE_CLEAR = '\x1b[2K'
    MOVE_TO_START = '\r'
    base_url = f'https://arpost.co/category/news/'
    headers = { 
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", 
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    } 
    max_page=None
    news_list: list[dict[str:str]] = []
    failed_news_links: list[str] = []
    parse_errors: dict[str, dict[str, int]] = {}

    def __init__(self, max_page=None):
        self.max_page = max_page

    def parse(self):
        url = self.base_url
        current_page=1
        while url and (self.max_page is None or current_page <= self.max_page):
            start_time = time.time()
            print(f'Parsing {url}... ', end=self.MOVE_TO_START)
            
            try:
                next_url = self.parseNewsAndNextUrl(url)
                time_taken = time.time() - start_time
                print(end=self.LINE_CLEAR)
                print(f'Successfully parsed {url} ({time_taken})')
                url = next_url
            except (ListLinkConnectionError, ParseListError) as e:
                self.addToParseErrors(url)
                print(end=self.LINE_CLEAR)
                print(f'Failed to parse {url}')

            current_page = current_page + 1

        return self.news_list, self.parse_errors, self.failed_news_links
    
    def addToParseErrors(self, url: str):
        tr = traceback.format_exc()
        if self.parse_errors.get(url) is None:
            self.parse_errors[url] = {}
        if self.parse_errors.get(url).get(str(tr)) is None:
            self.parse_errors[url][str(tr)] = 1
        else:
            self.parse_errors[url][str(tr)] = self.parse_errors.get(url).get(str(tr)) + 1
    
    def parseNewsAndNextUrl(self, url):
        try:
            list_html = self.parseDocumentFromLink(url)
            list_page = BeautifulSoup(list_html, 'lxml')
            posts = self.parseNewsList(list_page)

            for post in posts:
                try:
                    news = self.parseNews(post)
                    self.news_list.append(news)
                except (ParseContentError, ParseImageError) as e:
                    self.addToParseErrors(url)
                except (PostLinkConnectionError):
                    continue
            
            next_url = self.parseNextUrl(list_page)
            return next_url
        except requests.exceptions.RequestException as e:
            raise ListLinkConnectionError(e)
    
    def parseNews(self, post):
        try:
            title_block = post.find('h2', 'post-title')
            title = title_block.a.text
            datetime = post.find('time')['datetime']
            splitted_datetime = datetime.split('T')
            published_date = splitted_datetime[0]
            post_link = post.a['href']
        except AttributeError as e:
            raise ParseContentError(e)
        else:
            img_link = self.parseNewsImage(post_link)

            return dict(
                title=title,
                img_link=img_link,
                link=post_link,
                published_date=published_date,
                is_url_valid=True,
            )
        
    def parseNewsImage(self, post_link):
        try:
            post_html = self.parseDocumentFromLink(post_link)
            post_page = BeautifulSoup(post_html, 'lxml')
            banner = post_page.find('div', 'single-post-top')

            if banner:
                img_link = banner.img['src']
            else:
                post_img = post_page.find('div', 'single-post-thumb-outer')
                img_link = post_img.img['src']
        except AttributeError as e:
            raise ParseImageError(e)
        except requests.exceptions.RequestException as e:
            self.addToParseErrors(post_link)
            self.failed_news_links.append(post_link)
            raise PostLinkConnectionError(e)
        else:
            return img_link

    def parseNewsList(self, list_page):
        try:
            list = list_page.find('div', 'blog-listing-wrap')
            posts = list.find_all('article', class_='post-wrap post-grid post-grid-3')
            return posts
        except AttributeError as e:
            raise ParseListError(e)

    def parseNextUrl(self, list_page):
        try:
            next_url = None
            pagination = list_page.find('div', 'blog-pagination pagination-number')
            next_page = pagination.find('a', 'next page-numbers')
            if next_page:
                next_url = next_page['href']

            return next_url
        except AttributeError as e:
            raise ParseNextUrlError(e)
        
    def parseDocumentFromLink(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        list_html = response.text
        
        return list_html
    
