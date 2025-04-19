#!/usr/bin/env python3
import csv
import re
import sys
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

# region defaults


STUNDEN_CSV_COLUMN_DATE = 0
STUNDEN_CSV_COLUMN_START = 1
STUNDEN_CSV_COLUMN_PAUSE = 2
STUNDEN_CSV_COLUMN_END = 3
STUNDEN_CSV_COLUMN_PERSONS = 4
STUNDEN_CSV_COLUMN_PERSONS_PL = 5


# endregion


def get_input_args():
    effective_program_arguments = len(sys.argv) - 1
    if not 1 <= effective_program_arguments <= 2:
        message = f"Usage: python rechnung_intervals_to_durations_csv.py <csv_file_path>\n"
        sys.stderr.write(message)
        sys.exit(1)

    def get_argument_or_default(index: int, default: any):
        return sys.argv[index] if len(sys.argv) > index else default

    csv_file_path = sys.argv[1]
    first_rechnung_nr = int(get_argument_or_default(2, 1))
    return csv_file_path, first_rechnung_nr


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


WorkSessionInfo = Tuple[str, float, str, int, int]
RechnungInfo = List[WorkSessionInfo]
DateToRechnung = Dict[str, RechnungInfo]


def parse_csv(csv_file_path: str):
    csv_file = open(csv_file_path, mode='r')
    csv_reader = csv.reader(csv_file, delimiter=',')

    date_to_tuple_list: DateToRechnung = {}

    for line_index, line in enumerate(csv_reader):
        if len(line) == 0:
            continue

        first_field = line[0]
        if first_field.startswith("#") or (line_index == 0 and first_field in ['datum', 'date']):
            continue  # skip header and/or comment lines

        date = line[STUNDEN_CSV_COLUMN_DATE]
        start = line[STUNDEN_CSV_COLUMN_START]
        pause = line[STUNDEN_CSV_COLUMN_PAUSE]
        end = line[STUNDEN_CSV_COLUMN_END]
        persons = line[STUNDEN_CSV_COLUMN_PERSONS]
        persons_pl = line[STUNDEN_CSV_COLUMN_PERSONS_PL]

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
        tuple_list.append((start, pause, end, persons, persons_pl))

    return sorted(date_to_tuple_list.items(), key=lambda item: date_str_to_date(item[0]).strftime('%Y.%m.%d'))


def hour_string_to_decimal(value: str):
    hour, minutes = list(map(float, value.split(':')))
    minutes_per_hour = 60
    return Decimal(str(hour)) + (Decimal(str(minutes)) / Decimal(str(minutes_per_hour)))


def compute_values(date_list: List[Tuple[str, RechnungInfo]], first_rechnung_nr: int):
    computed_hours = []

    for i, (date, rechnung_infos) in enumerate(date_list):
        rechnung_nr = first_rechnung_nr + i
        print(f"\n\n\t### RECHNUNG NR: {rechnung_nr} {date} ###")
        for j, (start, pause, end, persons, persons_pl) in enumerate(rechnung_infos):
            if not (persons >= persons_pl >= 0):
                sys.stderr.write(f"Condition persons >= persons_pl >= 0 is not respected: {persons} >= {persons_pl} >= 0\n")
                exit(1)

            stunden = hour_string_to_decimal(end) - hour_string_to_decimal(start) - Decimal(str(pause))
            stunden = max(stunden, Decimal(str('4')))
            total_stunden = stunden * Decimal(str(persons))
            total_stunden_pl = stunden * Decimal(str(persons_pl))
            print("-" * 5 + f" PAGE {i + 1:02} START " + "-" * 5)
            print(f"{stunden} ST x {persons} P = {total_stunden} ST")
            print(f"PL x {persons_pl}")
            print()
            print(f"RECHNUNG {rechnung_nr}")
            print("-" * 5 + f" PAGE {i + 1:02} END " + "-" * 5)
            print()

            total_stunden_str = int(total_stunden) if total_stunden % 1 == 0 else total_stunden
            total_stunden_pl_str = int(total_stunden_pl) if total_stunden_pl % 1 == 0 else total_stunden_pl
            computed_hours.append(f"{date},{total_stunden_str},{total_stunden_pl_str}")

    print("\n".join(computed_hours))  # to compare replace in stunden.csv "[0-9]{7},[a-zA-Z ]+," with ""


def main():
    # TODO: change order of computing + fix page number
    #   TODO: [MAYBE ???] change how PL is shown: -||- x ? P = ?? ST PL
    # TODO: also include kn_nr and auf
    # TODO: add warning about different hours for different people for same (date, kn_nr)
    # TODO: move to rechnung_from_durations_csv.py
    # TODO: [AFTER MOVING to rechnung_from_durations_csv.py] use the args parser: <mode> <csv file> [<first rechnung nr>] [<price_per_stunden>]
    csv_file_path, first_rechnung_nr = get_input_args()
    date_list = parse_csv(csv_file_path)
    compute_values(date_list, first_rechnung_nr)


if __name__ == "__main__":
    main()
