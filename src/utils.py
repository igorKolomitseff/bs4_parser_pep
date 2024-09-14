import logging

from requests import RequestException

from constants import NOT_FIND_TAG_ERROR, REQUEST_ERROR
from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            REQUEST_ERROR.format(url=url),
            stack_info=True
        )


def find_tag(soup, tag=None, attrs=None, string='', find_type='find'):
    if find_type == 'find':
        searched_tag = soup.find(
            tag,
            attrs=(attrs or {}),
            string=(string or '')
        )
    elif find_type == 'find_parent':
        text = soup.find(string=string)
        searched_tag = (
            text.find_parent()
            if text
            else None
        )
    elif find_type == 'find_next_sibling':
        searched_tag = soup.find_next_sibling()
    else:
        raise ValueError(
            'Неверный тип поиска. '
            'Используйте "find", "find_parent" или "find_next_sibling".'
        )
    if searched_tag is None:
        logging.error(
            NOT_FIND_TAG_ERROR.format(tag=tag, attrs=attrs, string=string),
            stack_info=True
        )
        raise ParserFindTagException(
            NOT_FIND_TAG_ERROR.format(tag=tag, attrs=attrs, string=string)
        )
    return searched_tag
