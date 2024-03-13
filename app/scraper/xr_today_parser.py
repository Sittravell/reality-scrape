from __future__ import annotations
from bs4 import BeautifulSoup
import requests
import time
import traceback
from .parse_exceptions import ListLinkConnectionError, ParseListError, ParseContentError, PostLinkConnectionError, ParseTimeError, LoadMoreLinkConnectionError
import urllib.parse
import sys
from datetime import datetime
class XRTodayParser():
    LINE_CLEAR = '\x1b[2K'
    MOVE_TO_START = '\r'
    base_url = 'https://www.xrtoday.com/latest-news/'
    headers = { 
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", 
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    } 
    max_load_more=None
    load_more_posts_limit=100
    news_list: list[dict[str:str]] = []
    failed_news_links: list[str] = []
    parse_errors: dict[str, dict[str, int]] = {}

    def __init__(self, max_load_more=None):
        self.max_load_more = max_load_more
        
    def parse(self):
        try:
            url = self.base_url
            start_time = time.time()
            print(f'Parsing {url}... ', end=self.MOVE_TO_START)

            exclude_param = self.parseFromListPageAndReturnLoadMoreExcludeParam(url)

            time_taken = time.time() - start_time
            print(end=self.LINE_CLEAR)
            print(f'Successfully parsed {url} ({time_taken})')

            current_page_param = 1
            parsed_list = None

            while((parsed_list is None or len(parsed_list) > 0) and (self.max_load_more is None or current_page_param <= self.max_load_more)):
                url = self.getLoadMoreUrl(exclude_param, current_page_param)

                start_time = time.time()
                print(f'Parsing {url}... ', end=self.MOVE_TO_START)

                parsed_list = self.loadMorePostAndParse(url) 

                time_taken = time.time() - start_time
                print(end=self.LINE_CLEAR)
                print(f'Successfully parsed {url} ({time_taken})')

                current_page_param = current_page_param + 1

        except (ListLinkConnectionError, LoadMoreLinkConnectionError, ParseListError, ParseContentError, ParseTimeError) as e:
            self.addToParseErrors(url)
            print(end=self.LINE_CLEAR)
            print(f'Failed to parse {url}')

        return self.news_list, self.parse_errors, self.failed_news_links
    
    def addToParseErrors(self, url: str):
        tr = traceback.format_exc()
        if self.parse_errors.get(url) is None:
            self.parse_errors[url] = {}
        if self.parse_errors.get(url).get(str(tr)) is None:
            self.parse_errors[url][str(tr)] = 1
        else:
            self.parse_errors[url][str(tr)] = self.parse_errors.get(url).get(str(tr)) + 1
    
    def parseFromListPageAndReturnLoadMoreExcludeParam(self, url):
        try:
            list_html = self.parseDocumentFromLink(url)
            list_page = BeautifulSoup(list_html, 'lxml')

            self.parsePostList(list_page)

            load_more_block = list_page.find('a', 'load-more-posts')
            data_exclude_attr=load_more_block['data-exclude']
            exclude_param = urllib.parse.quote(data_exclude_attr)
            return exclude_param
        except requests.exceptions.RequestException as e:
            raise ListLinkConnectionError(e)
    
    def removeWhitespace(self, html: str):
        return "".join(line.strip() for line in html.split("\n")) 
    
    def parsePost(self, post):
        try:
            title_block = post.find('p', 'post-card-title')
            title = self.removeWhitespace(title_block.text)

            link_block = post.a

            img_container = link_block.div
            img_block = img_container.img
            img_link = img_block['src']

            post_link = link_block['href']
        except AttributeError as e:
            raise ParseContentError(e)
        else:
            edit_date = self.parseNewsTime(post_link)

            return dict(
                title=title,
                img_link=img_link,
                link=post_link,
                edit_date=edit_date,
                is_url_valid=True,
            )
        
    def parseNewsTime(self, post_link):
        try:
            post_html = self.parseDocumentFromLink(post_link)
            post_page = BeautifulSoup(post_html, 'lxml')
            
            time_container = post_page.find(id='article-meta-dates-favourite')
            time_text = time_container.p.text
            date=time_text[13:]

            parsed_date = datetime.strptime(date, '%B %d, %Y')
            formatted_date = parsed_date.strftime('%Y-%m-%d')
        except AttributeError as e:
            raise ParseTimeError(e)
        except requests.exceptions.RequestException as e:
            self.addToParseErrors(post_link)
            self.failed_news_links.append(post_link)
            raise PostLinkConnectionError(e)
        else:
            return formatted_date

    def parsePostList(self, list):
        try:
            posts = list.find_all('div', class_='post-card')
            parsed_list = []

            for post in posts:
                try:
                    post = self.parsePost(post)
                    self.news_list.append(post)
                    parsed_list.append(post)
                except (PostLinkConnectionError):
                    continue

            return parsed_list
        except AttributeError as e:
            raise ParseListError(e)

    def getLoadMoreUrl(self, exclude_param, current_page):
        return f'https://www.xrtoday.com/wp-admin/admin-ajax.php?action=td_load_more_post_ajax&ppp={self.load_more_posts_limit}&currentPage={current_page}&exclude={exclude_param}'
    
    def loadMorePostAndParse(self, load_more_url):
        try:
            more_posts_html = self.parseDocumentFromLink(load_more_url)
            more_posts = BeautifulSoup(more_posts_html, 'lxml')
            return self.parsePostList(more_posts)
        except requests.exceptions.RequestException as e:
            raise LoadMoreLinkConnectionError(e)
        
    def parseDocumentFromLink(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        list_html = response.text
        
        return list_html
    
