from pathlib import Path

BASE_DIR = Path(__file__).parent
BS4_PARSER = 'lxml'

MAIN_DOC_URL = 'https://docs.python.org/3/'
WHATS_NEW_URL_POSTFIX = 'whatsnew/'
DOWNLOAD_URL_POSTFIX = 'download.html'
PEP_URL = 'https://peps.python.org/'

TEXT_LINK_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
FILE_FORMAT_PATTERN = r'.+pdf-a4\.zip$'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUSES = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
