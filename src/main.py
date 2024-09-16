import logging
import re
from typing import List, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    BS4_PARSER,
    CLI_ARGS_INFO,
    DOWNLOADS_DIR,
    DOWNLOAD_URL_POSTFIX,
    EXPECTED_STATUS,
    FILE_FORMAT_PATTERN,
    FINISH_PARSER_WORKING_INFO,
    LATEST_VERSIONS_TABLE_COLUMN_HEADERS,
    MAIN_DOC_URL,
    MISMATCHED_STATUSES,
    NOT_FIND_TAG_ERROR,
    PEP_TABLE_COLUMN_HEADERS,
    PEP_URL,
    START_PARSER_WORKING_INFO,
    SUCCESS_ARCHIVE_DOWNLOAD,
    TEXT_LINK_PATTERN,
    WHATS_NEW_TABLE_COLUMN_HEADERS,
    WHATS_NEW_URL_POSTFIX
)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session: CachedSession) -> List[Tuple[str, ...]]:
    """Собирает информацию о нововведениях в версиях Python.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, WHATS_NEW_URL_POSTFIX)
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=BS4_PARSER)
    main_section = find_tag(
        soup,
        'section',
        {'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_section,
        'div',
        {'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    results = [WHATS_NEW_TABLE_COLUMN_HEADERS]
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, find_tag(section, 'a')['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=BS4_PARSER)
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )
    return results


def latest_versions(session: CachedSession) -> List[Tuple[str, ...]]:
    """Собирает информацию о статусах версий Python.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=BS4_PARSER)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all(name='a')
            break
    else:
        logging.error(
            NOT_FIND_TAG_ERROR.format(tag='ul', attrs=None, string=''),
            stack_info=True
        )
        raise ParserFindTagException(
            NOT_FIND_TAG_ERROR.format(tag='ul', attrs=None, string='')
        )
    results = [LATEST_VERSIONS_TABLE_COLUMN_HEADERS]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(TEXT_LINK_PATTERN, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session: CachedSession) -> List[Tuple[str, ...]]:
    """Скачивает архив с документацией Python.

    Параметры:
        session: Сессия для запросов к сайту.
    """
    downloads_url = urljoin(MAIN_DOC_URL, DOWNLOAD_URL_POSTFIX)
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=BS4_PARSER)
    main_tag = find_tag(
        soup,
        'div',
        {'role': 'main'}
    )
    table_tag = find_tag(
        main_tag,
        'table',
        {'class': 'docutils'}
    )
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(FILE_FORMAT_PATTERN)}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    response = get_response(session, archive_url)
    if response is None:
        return
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
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
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features=BS4_PARSER)
    main_section = find_tag(
        soup,
        'section',
        {'id': 'numerical-index'}
    )
    table = find_tag(
        main_section,
        'table',
        {'class': 'pep-zero-table'}
    )
    section_by_pep = table.tbody.find_all('tr')
    statuses_with_counts = {}
    for row in tqdm(section_by_pep):
        expected_status = find_tag(row, 'abbr').text[1:]
        pep_link = urljoin(PEP_URL, find_tag(row, 'a')['href'])
        response = get_response(session, pep_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features=BS4_PARSER)
        dt_tag = find_tag(
            soup,
            string=re.compile('Status'),
            find_type='find_parent'
        )
        current_status = find_tag(dt_tag, find_type='find_next_sibling').text
        if current_status not in statuses_with_counts:
            statuses_with_counts[current_status] = 1
        else:
            statuses_with_counts[current_status] += 1
        if current_status not in EXPECTED_STATUS[expected_status]:
            logging.info(
                MISMATCHED_STATUSES.format(
                    pep_link=pep_link,
                    current_status=current_status,
                    expected_status=EXPECTED_STATUS[expected_status]
                )
            )
    results = [PEP_TABLE_COLUMN_HEADERS]
    results.extend(
        sorted(
            statuses_with_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )
    results.append(('Total', sum(statuses_with_counts.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    """Запускает скрипт парсера."""
    configure_logging()
    logging.info(START_PARSER_WORKING_INFO)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(CLI_ARGS_INFO.format(args=args))
    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()
    results = MODE_TO_FUNCTION[args.mode](session)
    if results is not None:
        control_output(results, args)
    logging.info(FINISH_PARSER_WORKING_INFO)


if __name__ == '__main__':
    main()
