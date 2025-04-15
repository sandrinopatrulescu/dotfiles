#!/usr/bin/env python3
from __future__ import annotations

import argparse
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import List, final


class InputMode(Enum):
    INTERVAL = "interval",
    DURATION = "duration",

    @staticmethod
    def from_string(name: str) -> "InputMode":
        return InputMode[name.upper()]


@dataclass(frozen=True)
class Interval:
    invoice_date: datetime
    item_name: str
    start: str
    pause: Decimal
    end: str
    persons: int


@dataclass(frozen=True)
class Duration:
    page_nr: int
    invoice_date: datetime
    invoice_nr: int
    item_name: str
    hours: Decimal
    persons: int


@dataclass(frozen=True)
class ItemPriceComputation:
    hours: Decimal
    price_per_hour: Decimal


@dataclass(frozen=True)
class ItemPrice:
    value: Decimal
    details: str


@dataclass(frozen=True)
class Item:
    name: str
    price_computation: ItemPriceComputation | None
    price: ItemPrice


@dataclass(frozen=True)
class Invoice:
    date: datetime
    number: int
    items: List[Item]


class AppException(Exception):
    pass


class Template:
    # TODO: for input as direct string instead of csv path: default impl for ABSTRACT methods VS another template considered default

    @staticmethod
    @final
    def process_csv(template: Template, input_mode: InputMode, path_or_string: str, price_per_hour: Decimal,
                    first_invoice_nr: int, is_print_only: bool):
        template.__proces_csv(input_mode, path_or_string, price_per_hour, first_invoice_nr, is_print_only)

    @final
    def __proces_csv(self, input_mode: InputMode, path_or_string: str, price_per_hour: Decimal, first_invoice_nr: int,
                     is_print_only: bool):
        durations = self.__read_csv(input_mode, path_or_string)
        invoices = self.__durations_to_invoices(durations, price_per_hour, first_invoice_nr)

        issue_date = datetime.now()
        self.__invoices_to_output(invoices, issue_date, is_print_only)

    @final
    def __read_csv(self, input_mode: InputMode, path_or_string: str) -> List[Duration]:
        match input_mode:
            case InputMode.INTERVAL:
                intervals = self.read_interval_csv(path_or_string)
                durations = self.__intervals_to_durations(intervals)
            case InputMode.DURATION:
                durations = self.read_duration_csv(path_or_string)
            case _:
                raise AppException(f'Unexpected input mode: {input_mode}. Expected one of {list(InputMode)}')
        return durations

    @abstractmethod
    def read_interval_csv(self, path_or_string: str) -> List[Interval]:
        raise NotImplementedError  # TODO

    @abstractmethod
    def read_duration_csv(self, path_or_string: str) -> List[Duration]:
        raise NotImplementedError  # TODO

    # noinspection PyMethodMayBeStatic
    def minimum_hours(self) -> Decimal:
        return Decimal('0')

    def on_durations_computed(self, durations: List[Duration]):
        raise NotImplementedError()  # TODO: print info for table scans - computed duration (what rechnung_data_from_computation_csv.py is doing)

    @final
    def __intervals_to_durations(self, intervals: List[Interval]) -> List[Duration]:
        # TODO: calls upon OVERRIDEABLE adjust_duration
        raise NotImplementedError()  # TODO

    @final
    def __durations_to_invoices(self, durations: List[Duration], price_per_hour: Decimal, first_invoice_nr: int) -> \
            List[Invoice]:
        """
        Preconditions:
            ensure `adjust_duration_hours()` has been called
        """
        raise NotImplementedError()  # TODO

    @final
    def __invoices_to_output(self, invoices: List[Invoice], issue_date: datetime, is_print_only: bool):
        # TODO: print final results + generate docx+pdf

        # TODO: use template: header_text (left, right), bank account
        # TODO for thicker horizontal table border - use condition - is_new_row_group
        raise NotImplementedError()  # TODO


class PR(Template):
    MINIMUM_HOURS = '4'

    def read_interval_csv(self, path_or_string: str) -> List[Interval]:
        # TODO:
        #   - code PL as different interval
        #       - LATER group them by date and/or name
        #   - convert here kn_nr + auf to item_name
        raise NotImplementedError()

    def read_duration_csv(self, path_or_string: str) -> List[Duration]:
        # TODO
        #   - convert here kn_nr + auf to item_name
        #   - calls upon OVERRIDEABLE adjust_duration (overridden for PR)
        raise NotImplementedError()

    def minimum_hours(self) -> Decimal:
        return Decimal(PR.MINIMUM_HOURS)

    def on_durations_computed(self, durations: List[Duration]):
        raise NotImplementedError()  # TODO: print info for table scans - computed duration (what rechnung_data_from_computation_csv.py is doing)


class ER:
    pass


class GIC:  # TODO: PR(TemplateReceiver), GIC(TemplateSender)
    pass


class GIG:
    pass


templates = [PR, ER, GIC, GIG]


# region helpers pure
def is_number(s: str):
    try:
        float(s)
        return True
    except ValueError:
        return False


# endregion


# region input processing
def validate_price_per_hour(value: str):
    try:
        return Decimal(value)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"{value} is not a valid decimal number")


def validate_first_rechnung_number(value: str):
    if value.isdigit():
        return int(value)
    else:
        raise argparse.ArgumentTypeError(f"{value} is not a valid non-negative integer")


def parse_args():
    modes = list(map(lambda x: x.name.lower(), list(InputMode)))
    template_choices = list(map(lambda x: x.__name__.lower(), templates))

    # @formatter:off
    parser = argparse.ArgumentParser(description="Create invoices from CSV files or strings")

    parser.add_argument("mode", choices=modes, help=f"The mode to use: {', '.join(template_choices)}")
    parser.add_argument("content", type=str, help="CSV path or string with format: TBD")
    parser.add_argument("--price-per-hour", "--pph", type=validate_price_per_hour, help="Hourly rate (float).")
    parser.add_argument("--template", "-t", choices=template_choices, help=f"Template type ({', '.join(template_choices)}).")
    parser.add_argument("-first-invoice-nr", "--fin", type=validate_first_rechnung_number, help="First invoice number (non-negative integer).")
    parser.add_argument("--print", "-p", action="store_true", help="Print output only (no docs).")
    # @formatter:on

    return parser.parse_args()


def template_name_to_template(name: str) -> Template:
    return globals()[str(name).upper()]()


# endregion


def main():
    """
    TODO:
        - path_or_string -> lines/rows (auto detected if <content> is file path)
        - implement interval CSV reading for PR
        - ???
        - default price per template
        - ???
        - check todos from `rechnung_data_from_computation_csv.py`
        - parse content when string
            - interval "09:00,0.0,19:00;10:00,0.0;14:00"
            - duration "????"
            - args parse - direct string format - TBD
        - ER template
            NOTE that ER template requires grouping by item_name (not by date) (maybe swap them)

    """
    args = parse_args()
    print(f"args={args}")

    template = template_name_to_template(args.template)
    mode = InputMode.from_string(args.mode)

    Template.process_csv(template, mode, args.content, args.price_per_hour, args.fin, args.print)


if __name__ == "__main__":
    main()
