from typing import Optional

from bs4 import BeautifulSoup, Tag
from requests import RequestException
from requests_cache import AnyResponse, CachedSession

from constants import (
    FIND_NEXT_SIBLING,
    FIND_TAG_BY_NAME,
    FIND_TAG_BY_STRING
)
from exceptions import ParserFindTagException

NOT_FIND_TAG_ERROR = 'Не найден тег {tag} {attrs} {string}'
REQUEST_ERROR = 'Возникла ошибка при загрузке страницы {url} {error}'


def get_response(
    session: CachedSession,
    url: str,
    encoding: str = 'utf-8'
) -> Optional[AnyResponse]:
    """Получает ответ с сайта по url.
    Если возникает ошибка при получении ответа, то вызывается исключение.

    Параметры:
        session: Сессия для запросов к сайту.
        url: URL адрес страницы.
        encoding: Кодировка страницы.
    """
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as error:
        raise ConnectionError(
            REQUEST_ERROR.format(url=url, error=error)
        )


def get_soup(
    session: CachedSession,
    url: str,
    features='lxml'
) -> BeautifulSoup:
    """Получает HTML страницу, парсит её с помощью BeautifulSoup и возвращает
    разобранный HTML (soup).

    Параметры:
        session: Сессия для запросов к сайту.
        url: URL адрес страницы.
        features: Тип парсера.
    """
    return BeautifulSoup(get_response(session, url).text, features=features)


def find_tag_by_name(
    soup: BeautifulSoup,
    tag: str,
    attrs: dict,
    **kwargs
) -> Optional[Tag]:
    """Получает тег по имени.

    Параметры:
        soup: Проанализированный HTML документ.
        tag: HTML Тег.
        attrs: Атрибуты тега.
    """
    return soup.find(tag, attrs)


def find_tag_by_string(
    soup: BeautifulSoup,
    string: str,
    **kwargs
) -> Optional[Tag]:
    """Получает тег по строке внутри тега.

    Параметры:
        soup: Проанализированный HTML документ.
        string: Текст в теге.
    """
    text = soup.find(string=string)
    return text.find_parent() if text is not None else None


def find_next_sibling(
    soup: BeautifulSoup,
    **kwargs
) -> Optional[Tag]:
    """Получает следующий тег-сосед.

    Параметры:
        soup: Проанализированный HTML документ.
    """
    return soup.find_next_sibling()


FIND_TYPE_TO_FUNCTION = {
    FIND_TAG_BY_NAME: find_tag_by_name,
    FIND_TAG_BY_STRING: find_tag_by_string,
    FIND_NEXT_SIBLING: find_next_sibling
}


def find_tag(
    soup: BeautifulSoup,
    tag: Optional[str] = None,
    attrs: Optional[dict] = None,
    string: Optional[str] = None,
    find_type: str = FIND_TAG_BY_NAME
) -> Optional[Tag]:
    """Получает тег по заданным атрибутам.
    Если не находит тег, то выбрасывает исключение.

    Параметры:
        soup: Проанализированный HTML документ.
        tag: HTML Тег.
        attrs: Атрибуты тега.
        string: Текст в теге.
        find_type: Тип поиска.
    """
    searched_tag = FIND_TYPE_TO_FUNCTION[find_type](
        soup,
        tag=tag if tag is not None else '',
        attrs=attrs if attrs is not None else {},
        string=string if string is not None else ''
    )
    if searched_tag is None:
        raise ParserFindTagException(
            NOT_FIND_TAG_ERROR.format(tag=tag, attrs=attrs, string=string)
        )
    return searched_tag
