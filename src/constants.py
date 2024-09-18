from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
RESULTS_DIR = 'results'
DOWNLOADS_DIR = 'downloads'
OUTPUT_FILE = '{parser_mode}_{now_formatted}.csv'

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
WHATS_NEW_URL_POSTFIX = 'whatsnew/'
DOWNLOAD_URL_POSTFIX = 'download.html'

FIND_TAG_BY_NAME = 'find_tag_by_name'
FIND_TAG_BY_STRING = 'find_tag_by_string'
FIND_NEXT_SIBLING = 'find_next_sibling'
OUTPUT_TO_FILE = 'file'
OUTPUT_TO_PRETTY_TABLE = 'pretty'

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

FILE_DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_OUTPUT_FORMAT = (
    '%(asctime)s [%(levelname)s]: %(funcName)s, '
    'строка %(lineno)d - %(message)s'
)
LOG_DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'
