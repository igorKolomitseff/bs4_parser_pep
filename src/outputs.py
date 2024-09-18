import csv
import datetime as dt
import logging
from argparse import Namespace
from typing import List, Tuple

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    FILE_DATETIME_FORMAT,
    OUTPUT_FILE,
    OUTPUT_TO_FILE,
    OUTPUT_TO_PRETTY_TABLE,
    RESULTS_DIR
)

SUCCESS_FILE_CREATED = 'Файл с результатами был сохранён: {file_path}'


def pretty_output(results: List[Tuple[str, ...]], *args) -> None:
    """
    Выводит данные в терминал в формате PrettyTable.

    Параметры:
        results: Результаты парсинга.
    """
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: List[Tuple[str, ...]], cli_args: Namespace) -> None:
    """Сохраняет данные в файл.

    Параметры:
        results: Результаты парсинга.
        cli_args: Аргументы командной строки.
    """
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / OUTPUT_FILE.format(
        parser_mode=cli_args.mode,
        now_formatted=dt.datetime.now().strftime(FILE_DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(SUCCESS_FILE_CREATED.format(file_path=file_path))


def default_output(results: List[Tuple[str, ...]], *args) -> None:
    """
    Выводит данные в терминал построчно.

    Параметры:
        results: Результаты парсинга.
    """
    for row in results:
        print(*row)


OUTPUT_TO_FUNCTION = {
    OUTPUT_TO_PRETTY_TABLE: pretty_output,
    OUTPUT_TO_FILE: file_output,
    None: default_output
}


def control_output(
    results: List[Tuple[str, ...]],
    cli_args: Namespace
) -> None:
    """Контролирует вывод результатов парсинга.

    Параметры:
        results: Результаты парсинга.
        cli_args: Аргументы командной строки.
    """
    OUTPUT_TO_FUNCTION[cli_args.output](results, cli_args)
