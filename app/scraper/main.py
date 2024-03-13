from .ar_post_parser import ARPostParser
from .xr_today_parser import XRTodayParser
from ..database.helpers import submit_parsed_list, submit_parse_errors, submit_invalid_urls

def getParsers():
    return [
        ARPostParser(),
        XRTodayParser()
    ]

def main():
    parsers = getParsers()

    all_news_list=[]
    all_parse_errors={}
    all_failed_links=[]

    for parser in parsers:
        news_list, parse_errors, failed_links = parser.parse()
        all_news_list.extend(news_list)
        all_parse_errors.update(parse_errors)
        all_failed_links.extend(failed_links)

    print('END OF PARSING')

    submit_parsed_list(all_news_list)
    submit_invalid_urls(all_failed_links)
    submit_parse_errors(all_parse_errors)

if __name__ == '__main__':
    main()