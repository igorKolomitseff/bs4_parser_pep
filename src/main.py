import logging
import re
from collections import defaultdict
from typing import List, Tuple
from urllib.parse import urljoin

from requests import RequestException
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    DOWNLOADS_DIR,
    DOWNLOAD_URL_POSTFIX,
    EXPECTED_STATUS,
    FIND_NEXT_SIBLING,
    FIND_TAG_BY_STRING,
    MAIN_DOC_URL,
    PEP_URL,
    WHATS_NEW_URL_POSTFIX
)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import get_soup, get_response, find_tag


START_PARSER_WORKING = 'Парсер запущен!'
CLI_ARGS = 'Аргументы командной строки: {args}'
FINISH_PARSER_WORKING = 'Парсер завершил работу.'
NOT_FIND_TAG_ERROR = 'Не найден тег {tag} {attrs} {string}'
REQUEST_ERROR = 'Возникла ошибка при загрузке страницы {url} {error}'
SUCCESS_ARCHIVE_DOWNLOAD = (
    'Архив был загружен и сохранён: {archive_path}'
)
MISMATCHED_STATUS = (
    'Несовпадающие статусы:\n'
    '{pep_link}\n'
    'Статус в карточке: {current_status}\n'
    'Ожидаемые статусы: {expected_status}\n'
)
MAIN_ERROR_MESSAGE = 'Сбой в работе программы: {error}'

WHATS_NEW_TABLE_COLUMN_HEADERS = (
    'Ссылка на статью', 'Заголовок', 'Редактор, автор'
)
LATEST_VERSIONS_TABLE_COLUMN_HEADERS = (
    'Ссылка на документацию', 'Версия', 'Статус'
)
PEP_TABLE_COLUMN_HEADERS = (
    'Статус', 'Количество'
)


def whats_new(session: CachedSession) -> List[Tuple[str, ...]]:
    """Собирает информацию о нововведениях в версиях Python.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, WHATS_NEW_URL_POSTFIX)
    results = [WHATS_NEW_TABLE_COLUMN_HEADERS]
    unavailable_links = []
    for a_tag in tqdm(get_soup(session, whats_new_url).select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > '
        'a[href!="changelog.html"]'
    )):
        version_link = urljoin(whats_new_url, a_tag['href'])
        try:
            soup = get_soup(session, version_link)
        except RequestException as error:
            unavailable_links.append(
                REQUEST_ERROR.format(url=version_link, error=error)
            )
            continue
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )
    logging.error('\n'.join(unavailable_links))
    return results


def latest_versions(session: CachedSession) -> List[Tuple[str, ...]]:
    """Собирает информацию о статусах версий Python.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    for ul in get_soup(session, MAIN_DOC_URL).select(
        'div.sphinxsidebarwrapper ul'
    ):
        if 'All versions' in ul.text:
            a_tags = ul.find_all(name='a')
            break
    else:
        raise ParserFindTagException(
            NOT_FIND_TAG_ERROR.format(tag='ul', attrs=None, string=None)
        )
    results = [LATEST_VERSIONS_TABLE_COLUMN_HEADERS]
    for a_tag in a_tags:
        text_match = re.search(
            r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)',
            a_tag.text
        )
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session: CachedSession) -> None:
    """Скачивает архив с документацией Python.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    downloads_url = urljoin(MAIN_DOC_URL, DOWNLOAD_URL_POSTFIX)
    pdf_a4_tag = get_soup(session, downloads_url).select_one(
        'div[role="main"] table.docutils a[href$="pdf-a4.zip"]'
    )
    if pdf_a4_tag is None:
        raise ParserFindTagException(
            NOT_FIND_TAG_ERROR.format(
                tag='a', attrs={'href$': 'pdf-a4.zip'}, string=None
            )
        )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    response = get_response(session, archive_url)
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / archive_url.split('/')[-1]
    with open(archive_path, 'wb') as zip_file:
        zip_file.write(response.content)
    logging.info(
        SUCCESS_ARCHIVE_DOWNLOAD.format(archive_path=archive_path)
    )


def pep(session: CachedSession) -> List[Tuple[str, ...]]:
    """Собирает информацию о статусах документов PEP.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    results = defaultdict(int)
    unavailable_links = []
    mismatched_statuses = []
    for row in tqdm(get_soup(session, PEP_URL).select(
        '#numerical-index table.pep-zero-table tbody tr'
    )):
        expected_status = find_tag(row, 'abbr').text[1:]
        pep_link = urljoin(PEP_URL, find_tag(row, 'a')['href'])
        try:
            soup = get_soup(session, pep_link)
        except RequestException as error:
            unavailable_links.append(
                REQUEST_ERROR.format(url=pep_link, error=error)
            )
            continue
        current_status = find_tag(
            find_tag(
                soup,
                string=re.compile('Status'),
                find_type=FIND_TAG_BY_STRING
            ),
            find_type=FIND_NEXT_SIBLING
        ).text
        results[current_status] += 1
        if current_status not in EXPECTED_STATUS[expected_status]:
            mismatched_statuses.append(
                MISMATCHED_STATUS.format(
                    pep_link=pep_link,
                    current_status=current_status,
                    expected_status=EXPECTED_STATUS[expected_status]
                )
            )
    logging.error('\n'.join(unavailable_links))
    logging.info('\n'.join(mismatched_statuses))
    return [
        PEP_TABLE_COLUMN_HEADERS,
        *results.items(),
        ('Всего', sum(results.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    """Запускает скрипт парсера."""
    try:
        configure_logging()
        logging.info(START_PARSER_WORKING)
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(CLI_ARGS.format(args=args))
        session = CachedSession()
        if args.clear_cache:
            session.cache.clear()
        results = MODE_TO_FUNCTION[args.mode](session)
        if results is not None:
            control_output(results, args)
        logging.info(FINISH_PARSER_WORKING)
    except Exception as error:
        logging.exception(
            MAIN_ERROR_MESSAGE.format(error=error),
            stack_info=True
        )


if __name__ == '__main__':
    main()
