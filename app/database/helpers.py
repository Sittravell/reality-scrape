from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import select
from .news import News
from .parse_error import ParseError
import requests
from dotenv import dotenv_values

cfg=dotenv_values()

def getRequestOptions(relative_url: str):
    url = cfg['PROD_API_URL'] + relative_url
    secret = cfg['PARSER_SECRET']
    headers = { 'Parser-Secret': secret }

    return url, headers


def submit_parsed_list(news_list: list[dict[str: str]]):
    if news_list == []:
        return
    
    url, headers = getRequestOptions('/api/news')
    payload = dict(posts=news_list)
    requests.post(url, headers=headers, json=payload)
    
def submit_parse_errors(parse_errors: dict[str,dict[str, int]]):
    parse_errors_rows: list[dict[str:str]] = []

    for url in parse_errors:
        for m in parse_errors[url]:
            count = parse_errors[url][m]
            parse_errors_rows.append(dict(
                link=url,
                error=m,
                count=count,
            ))

    if parse_errors_rows == []:
        return
    
    url, headers = getRequestOptions('/api/parse_error')
    payload = dict(errors=parse_errors_rows)
    requests.post(url, headers=headers, json=payload)

def submit_invalid_urls(failed_links: list[str]):
    if failed_links == []:
        return
    
    failed_link_rows = [dict(link=url, is_url_valid=False) for url in failed_links]

    url, headers = getRequestOptions('/api/news/links')
    payload = dict(links=failed_link_rows)
    requests.put(url, headers=headers, json=payload)

def store_parsed_list(db: Session, news_list: list[dict[str:str]]):
    if news_list == []:
        return

    db.begin()
    stmt = insert(News).values(news_list)
    stmt = stmt.on_duplicate_key_update(
        title=stmt.inserted.title,
        link=stmt.inserted.link,
        img_link=stmt.inserted.img_link,
        time=stmt.inserted.time,
        is_url_valid=stmt.inserted.is_url_valid,
        updated_at=stmt.inserted.updated_at,
    )
    db.execute(stmt)
    db.commit()

    return news_list

def store_parse_errors(db: Session, parse_errors: dict[str,dict[str, int]]):
    parse_errors_rows: list[dict[str:str]] = []

    for url in parse_errors:
        for m in parse_errors[url]:
            count = parse_errors[url][m]
            parse_errors_rows.append(dict(
                link=url,
                error=m,
                count=count,
            ))

    if parse_errors_rows == []:
        return
    
    db.begin()
    stmt = insert(ParseError).values(parse_errors_rows)
    db.execute(stmt)
    db.commit()

def store_invalid_urls(db: Session, failed_links: list[str]):
    if failed_links == []:
        return
    
    failed_link_rows = [dict(link=url, is_url_valid=False) for url in failed_links]

    db.begin()
    stmt = insert(News).values(failed_link_rows)
    stmt = stmt.on_duplicate_key_update(
        is_url_valid=stmt.inserted.is_url_valid,
        updated_at=stmt.inserted.updated_at,
    )
    db.execute(stmt)
    db.commit()

def retrieve_news(db: Session):
    stmt = select(News).order_by(News.time.desc())
    rows = db.execute(stmt).scalars().all()
    res = [ transformToResponse(news) for news in rows ]
    return res

def transformToResponse(news: News):
    return dict(
        title=news.title,
        link=news.link,
        img_link=news.img_link,
        time=news.time,
    )