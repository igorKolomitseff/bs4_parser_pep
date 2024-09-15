import argparse
import logging
from logging.handlers import RotatingFileHandler
from typing import KeysView

from constants import (
    LOG_DATETIME_FORMAT,
    LOG_DIR,
    LOG_FILE,
    LOG_OUTPUT_FORMAT
)


def configure_argument_parser(
    available_modes: KeysView[str]
) -> argparse.ArgumentParser:
    """
    Настраивает парсинг аргументов командной строки.

    Параметры:
        available_modes: Режимы работы парсера.
    """
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша',
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging() -> None:
    """Настраивает логирование."""
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        datefmt=LOG_DATETIME_FORMAT,
        format=LOG_OUTPUT_FORMAT,
        level=logging.INFO,
        handlers=(
            RotatingFileHandler(
                LOG_FILE, maxBytes=10 ** 6, backupCount=5
            ),
            logging.StreamHandler()
        ),
    )
