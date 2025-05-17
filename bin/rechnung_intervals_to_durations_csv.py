#!/usr/bin/env python3
import csv
import os
import re
import sys
import tempfile
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

import pyperclip

# region defaults
ROW_WIDTH_TO_COLUMN_NAME_TO_COLUMN_INDEX = {
    6: {
        'DATE': 0,
        'START': 1,
        'PAUSE': 2,
        'END': 3,
        'PERSONS': 4,
        'PERSONS_PL': 5,
    },
    8: {
        'DATE': 0,
        'KN_NR': 1,
        'BAU': 2,
        'START': 3,
        'PAUSE': 4,
        'END': 5,
        'PERSONS': 6,
        'PERSONS_PL': 7,
    },
}

valid_row_widths = ROW_WIDTH_TO_COLUMN_NAME_TO_COLUMN_INDEX.keys()


def is_valid_row_width(row_width: int) -> bool:
    return row_width in valid_row_widths


def get_column_index(row_width: int, column_name: str) -> int:
    return ROW_WIDTH_TO_COLUMN_NAME_TO_COLUMN_INDEX[row_width].get(column_name)


# endregion


def get_input_args():
    effective_program_arguments = len(sys.argv) - 1
    if not 1 <= effective_program_arguments <= 3:
        message = f"Usage: python rechnung_intervals_to_durations_csv.py <csv_file_path> [<first rechnung nr>=1] [--interactive]\n"
        sys.stderr.write(message)
        sys.exit(1)

    def get_argument_or_default(index: int, default: any):
        return sys.argv[index] if len(sys.argv) > index else default

    csv_file_path = sys.argv[1]
    first_rechnung_nr = int(get_argument_or_default(2, 1))
    interactive = get_argument_or_default(3, "") == "--interactive"
    return csv_file_path, first_rechnung_nr, interactive


def date_str_to_date(date_str: str):
    return datetime.strptime(date_str, "%d.%m.%Y")


def is_valid_date(date_str: str):
    try:
        if not bool(re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str)):
            return False

        date_str_to_date(date_str)
        return True
    except ValueError:
        return False


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_valid_hour_format(s):
    try:
        datetime.strptime(s, "%H:%M")
        return True
    except ValueError:
        return False


WorkSessionInfo = Tuple[str, str, str, float, str, int, int]
RechnungInfo = List[WorkSessionInfo]
DateToRechnung = Dict[str, RechnungInfo]


def parse_csv(csv_file_path: str):
    csv_file = open(csv_file_path, mode='r')
    csv_reader = csv.reader(csv_file, delimiter=',')

    date_to_tuple_list: DateToRechnung = {}

    for line_index, line in enumerate(csv_reader):
        row_width = len(line)
        if row_width == 0:
            continue

        first_field = line[0]
        if first_field.startswith("#") or (line_index == 0 and first_field in ['datum', 'date']):
            continue  # skip header and/or comment lines

        def get_column_value(column_name: str, default_value=None):
            if not is_valid_row_width(row_width):
                message = f"Invalid row width: {row_width} at line {line_index + 1}. Should be one of {valid_row_widths}"
                raise ValueError(message)

            column_index = get_column_index(row_width, column_name)
            return default_value if column_index is None else line[column_index]

        date = get_column_value('DATE')
        kn_nr = get_column_value('KN_NR', 'KN_NR')
        bau = get_column_value('BAU', 'BAU')
        start = get_column_value('START')
        pause = get_column_value('PAUSE')
        end = get_column_value('END')
        persons = get_column_value('PERSONS')
        persons_pl = get_column_value('PERSONS_PL')

        if not is_valid_date(date):
            raise ValueError(f"Invalid date {date} at line {line_index + 1}")
        if not is_valid_hour_format(start):
            raise ValueError(f"Invalid start {start} at line {line_index + 1}")
        if not is_number(pause):
            raise ValueError(f"Invalid pause {pause} at line {line_index + 1}")
        if not is_valid_hour_format(end):
            raise ValueError(f"Invalid end {end} at line {line_index + 1}")
        if not persons.isdigit():
            raise ValueError(f"Invalid persons {persons} at line {line_index + 1}")
        if not persons_pl.isdigit():
            raise ValueError(f"Invalid persons_pl {persons_pl} at line {line_index + 1}")

        pause = float(pause)
        persons = int(persons)
        persons_pl = int(persons_pl)

        tuple_list = date_to_tuple_list.setdefault(date, [])
        tuple_list.append((kn_nr, bau, start, pause, end, persons, persons_pl))

    return sorted(date_to_tuple_list.items(), key=lambda item: date_str_to_date(item[0]).strftime('%Y.%m.%d'))


def hour_string_to_decimal(value: str):
    hour, minutes = list(map(float, value.split(':')))
    minutes_per_hour = 60
    return Decimal(str(hour)) + (Decimal(str(minutes)) / Decimal(str(minutes_per_hour)))


def compute_time_difference(start: Decimal, end: Decimal):
    hours_per_day = Decimal('24')
    return (end - start) + (end < start) * hours_per_day


def compute_values(date_list: List[Tuple[str, RechnungInfo]], first_rechnung_nr: int, interactive: bool):
    computed_hours_strings = []
    page_nr = 0

    nr_of_pages = sum(map(lambda x: len(x[1]), date_list))
    for i, (date, rechnung_infos) in enumerate(date_list):
        rechnung_nr = first_rechnung_nr + i
        print("\n" * 3 + f"### RECHNUNG NR: {rechnung_nr} {date} ###\n")
        for j, (kn_nr, bau, interval_start, pause, interval_end, persons, persons_pl) in enumerate(rechnung_infos):
            if not (persons >= persons_pl >= 0):
                sys.stderr.write(
                    f"Condition persons >= persons_pl >= 0 is not respected: {persons} >= {persons_pl} >= 0\n")
                exit(1)

            interval_start_decimal = hour_string_to_decimal(interval_start)
            interval_end_decimal = hour_string_to_decimal(interval_end)
            stunden = compute_time_difference(interval_start_decimal, interval_end_decimal) - Decimal(str(pause))
            stunden = max(stunden, Decimal(str('4')))
            total_stunden = stunden * Decimal(str(persons))
            total_stunden_pl = stunden * Decimal(str(persons_pl))
            page_nr += 1

            text_to_copy = f"{stunden} ST x {persons} P = {total_stunden} ST" + '\n'
            text_to_copy += f"PL x {persons_pl}" + '\n'
            text_to_copy += '\n'
            text_to_copy += f"RECHNUNG {rechnung_nr}"

            print(" " * 3 + f" PAGE {page_nr:02}/{nr_of_pages:00}\n")
            print(text_to_copy)
            print()
            while interactive:
                pyperclip.copy(text_to_copy)
                if input("Text copied to clipboard. Type 'ok' to continue: ") == "ok":
                    break
            print("\n" * 3)

            total_stunden_str = int(total_stunden) if total_stunden % 1 == 0 else total_stunden
            total_stunden_pl_str = int(total_stunden_pl) if total_stunden_pl % 1 == 0 else total_stunden_pl
            computed_hours_strings.append(f"{date},{kn_nr},{bau},{total_stunden_str},{total_stunden_pl_str}")
    computed_hours_strings.append("# date,kn_nr,bau,hours,hours_pl")
    computed_hours_strings.append("# example: 09.05.2025,2503052,ab ,16,4")

    computed_hours_strings_concatenated = "\n".join(computed_hours_strings)
    print(computed_hours_strings_concatenated)  # to compare replace in stunden.csv "[0-9]{7},[a-zA-Z ]+," with ""
    print()

    last_rechnung_nr = first_rechnung_nr + len(date_list) - 1
    stunden_file = f'rechungen_{first_rechnung_nr:03}-bis-{last_rechnung_nr:03}_stunden.pdf'
    print()
    print()
    while interactive:
        pyperclip.copy(stunden_file)
        if input(f"Prepare {stunden_file} (copied to clipboard) and type 'ok' to continue: ") == "ok":
            if not os.path.isfile(stunden_file):
                print(f'{stunden_file} not found')
                continue
            break
    print(stunden_file)
    print()

    # write computed_hours_strings_concatenated to a temporary files
    temp_file_name = next(tempfile._get_candidate_names()) + '.csv'
    temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
    file = open(temp_file_path, 'w')
    file.write(computed_hours_strings_concatenated + "\n")
    file.close()
    print(f"maybe run: cp {temp_file_path} durations.csv")


def main():
    # TODO: change order of computing + fix page number
    #   TODO: [MAYBE ???] change how PL is shown: -||- x ? P = ?? ST PL
    # TODO: also include kn_nr and auf
    # TODO: add warning about different hours for different people for same (date, kn_nr)
    # TODO: move to rechnung_from_durations_csv.py
    # TODO: [AFTER MOVING to rechnung_from_durations_csv.py] use the args parser: <mode> <csv file> [<first rechnung nr>] [<price_per_stunden>]
    csv_file_path, first_rechnung_nr, interactive = get_input_args()
    date_list = parse_csv(csv_file_path)
    compute_values(date_list, first_rechnung_nr, interactive)


if __name__ == "__main__":
    main()
