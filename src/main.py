import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    BS4_PARSER,
    DOWNLOAD_URL_POSTFIX,
    FILE_FORMAT_PATTERN,
    MAIN_DOC_URL,
    TEXT_LINK_PATTERN,
    WHATS_NEW_URL_POSTFIX
)
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
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

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
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


def latest_versions(session):
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
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(TEXT_LINK_PATTERN, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append((link, version, status))

    return results


def download(session):
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
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    with open(archive_path, 'wb') as zip_file:
        zip_file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    results = MODE_TO_FUNCTION[args.mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
