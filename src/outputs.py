import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    FILE_DATETIME_FORMAT,
    OUTPUT_FILE,
    RESULTS_DIR,
    SUCCESS_FILE_CREATED
)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / OUTPUT_FILE.format(
        parser_mode=cli_args.mode,
        now_formatted=dt.datetime.now().strftime(FILE_DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, dialect='unix')
        writer.writerows(results)
    logging.info(SUCCESS_FILE_CREATED.format(file_path=file_path))


def default_output(results):
    for row in results:
        print(*row)


def control_output(results, cli_args):
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)
