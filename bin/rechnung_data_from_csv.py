#!/usr/bin/env python3
import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# region defaults


PRICE_PER_STUNDEN = 25.0
PRICE_PER_STUNDEN_PL = 3.0
VAT_RATE = 19


# endregion


def get_input_args():
    if not 1 <= len(sys.argv) - 1 <= 3:
        message = f"Usage: python rechnung_data_from_csv.py <csv_file_path> [<first_rechnung_nr>=1] [<price_per_stunden>={PRICE_PER_STUNDEN}]\n"
        sys.stderr.write(message)
        sys.exit(1)

    def get_argument_or_default(index: int, default: any):
        return sys.argv[index] if len(sys.argv) > index else default

    csv_file_path = sys.argv[1]
    first_rechnung_nr = int(get_argument_or_default(2, 1))
    price_per_stunden = float(get_argument_or_default(3, PRICE_PER_STUNDEN))
    return csv_file_path, first_rechnung_nr, price_per_stunden


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


WorkSessionInfo = Tuple[str, str, float, float]
RechnungInfo = List[WorkSessionInfo]
DateToRechnung = Dict[str, RechnungInfo]


def parse_csv(csv_file_path: str):
    csv_file = open(csv_file_path, mode='r')
    csv_reader = csv.reader(csv_file, delimiter=',')

    date_to_tuple_list: DateToRechnung = {}

    for i, line in enumerate(csv_reader):
        if line[0] == 'datum':
            continue  # skip header
        if not is_valid_date(line[0]):
            raise ValueError(f"Invalid date {line[0]} at line {i + 1}")
        if not all(map(is_number, [line[1]] + line[3:])):  # skip bau
            raise ValueError(f"Invalid numbers at line {i + 1}")

        date = line[0]
        kn_nr = line[1]  # ab, auf, um
        bau = line[2].strip()
        stunden = float(line[3])
        stunden_pl = float(line[4])
        tuple_list = date_to_tuple_list.setdefault(date, [])
        tuple_list.append((kn_nr, bau, stunden, stunden_pl))

    return sorted(date_to_tuple_list.items(), key=lambda item: date_str_to_date(item[0]).strftime('%Y.%m.%d'))


def compute_values(date_list: List[Tuple[str, RechnungInfo]], first_rechnung_nr: int, price_per_stunden: float):
    format_row_string = lambda x, y, z: f"{x:<32}\t{y:>25}\t{z:<25}\n"
    format_computation_column = lambda hours, price: f"{hours:04.2f} St x {price:5.2f} Euro".replace(".", ",")
    format_final_price = lambda price: f"{price:7.2f}".replace(".", ",")
    format_price_no_justify = lambda price: f"{price:.2f}".replace(".", ",")
    row_width = 83
    row_group_separator = "-" * row_width + "\n"

    rechnung_prices = []

    print(datetime.now().strftime("%d.%m.%Y") + "\n")

    for i, (date, tuple_list) in enumerate(date_list):
        result = ""

        total_stunden_price = 0
        total_stunden_pl = 0
        total_stunden_pl_price = 0

        for j, (kn_nr, bau, stunden, stunden_pl) in enumerate(tuple_list):
            kn_price = stunden * price_per_stunden
            total_stunden_price += kn_price
            total_stunden_pl += stunden_pl

            bau_string = ' / '.join(map(lambda x: x.strip().capitalize() + 'bau', bau.split('+')))
            info_column = f"{j + 1}. KN NR: {kn_nr} {bau_string}"
            computation_column = format_computation_column(stunden, price_per_stunden)
            result_column = f"{format_final_price(kn_price)} Euro netto"

            result += format_row_string(info_column, computation_column, result_column)

        if total_stunden_pl > 0:
            info_column = f'{len(tuple_list) + 1}. Projekt Leiter Zuschlag'
            computation_column = format_computation_column(total_stunden_pl, PRICE_PER_STUNDEN_PL)
            total_stunden_pl_price = total_stunden_pl * PRICE_PER_STUNDEN_PL
            result_column = f"{format_final_price(total_stunden_pl_price)} Euro netto"
            result += format_row_string(info_column, computation_column, result_column)

        result += row_group_separator

        arbeitsleistung_netto = total_stunden_price + total_stunden_pl_price
        result_column = f"{format_final_price(arbeitsleistung_netto)} Euro netto"
        result += format_row_string("Arbeitsleistung Netto:", "", result_column)

        mehrwertsteuer_not_rounded = VAT_RATE / 100 * arbeitsleistung_netto
        mehrwertsteuer = round(mehrwertsteuer_not_rounded, 2)
        row_end = f" ({mehrwertsteuer_not_rounded})" if len(str(mehrwertsteuer_not_rounded).split('.')[1]) > 2 else ""
        result += format_row_string("MwSt. 19%:", "", f"{format_final_price(mehrwertsteuer)} Euro" + row_end)

        result += row_group_separator

        gesamtbetrag = arbeitsleistung_netto + mehrwertsteuer
        result += format_row_string("Gesamtbetrag:", "", f"{format_final_price(gesamtbetrag)} Euro Brutto")

        rechnung_prices.append(gesamtbetrag)

        print(f"RECHNUNG {first_rechnung_nr + i}\t{date}")
        print(result + "\n" * 2)

    total = sum(rechnung_prices)
    total_formatted = format_price_no_justify(total)
    summation = ' + '.join(map(lambda price: f'{format_price_no_justify(price)}', rechnung_prices))
    print(f"total: {summation} = {total_formatted}")

    print()

    last_rechnung_nr = first_rechnung_nr + len(date_list) - 1
    date_range = f"{date_list[0][0]} - {date_list[-1][0]}"
    print(f"email subject: rechnungen {first_rechnung_nr} bis {last_rechnung_nr} | {date_range}")
    print(f"email body: Ins gesamt {total_formatted} Euro.")


def main():
    csv_file_path, first_rechnung_nr, price_per_stunden = get_input_args()
    date_list = parse_csv(csv_file_path)
    compute_values(date_list, first_rechnung_nr, price_per_stunden)


if __name__ == "__main__":
    main()
