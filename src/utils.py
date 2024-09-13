import logging

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
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
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
