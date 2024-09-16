from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
RESULTS_DIR = 'results'
DOWNLOADS_DIR = 'downloads'
OUTPUT_FILE = '{parser_mode}_{now_formatted}.csv'

BS4_PARSER = 'lxml'

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
WHATS_NEW_URL_POSTFIX = 'whatsnew/'
DOWNLOAD_URL_POSTFIX = 'download.html'

TEXT_LINK_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
FILE_FORMAT_PATTERN = r'.+pdf-a4\.zip$'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

WHATS_NEW_TABLE_COLUMN_HEADERS = (
    'Ссылка на статью', 'Заголовок', 'Редактор, автор'
)
LATEST_VERSIONS_TABLE_COLUMN_HEADERS = (
    'Ссылка на документацию', 'Версия', 'Статус'
)
PEP_TABLE_COLUMN_HEADERS = (
    'Статус', 'Количество'
)

LOG_OUTPUT_FORMAT = (
    '%(asctime)s [%(levelname)s]: %(funcName)s, '
    'строка %(lineno)d - %(message)s'
)
LOG_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

FILE_DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

START_PARSER_WORKING_INFO = 'Парсер запущен!'
CLI_ARGS_INFO = 'Аргументы командной строки: {args}'
FINISH_PARSER_WORKING_INFO = 'Парсер завершил работу.'
REQUEST_ERROR = 'Возникла ошибка при загрузке страницы {url}'
WRONG_FIND_TYPE = 'Неверный тип поиска'
NOT_FIND_TAG_ERROR = 'Не найден тег {tag} {attrs} {string}'
SUCCESS_FILE_CREATED = (
    'Файл с результатами был сохранён: {file_path}'
)
SUCCESS_ARCHIVE_DOWNLOAD = (
    'Архив был загружен и сохранён: {archive_path}'
)
MISMATCHED_STATUSES = (
    'Несовпадающие статусы:\n'
    '{pep_link}\n'
    'Статус в карточке: {current_status}\n'
    'Ожидаемые статусы: {expected_status}\n'
)
