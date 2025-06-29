#!/usr/bin/env python3
import argparse
import os
import pydoc
import tempfile
from decimal import Decimal
from enum import Enum
from typing import Any, Dict

import requests
from dotenv import load_dotenv


def load_env():
    env_file = os.environ.get("ALEX_RECHNUNG_ENV_FILE")
    load_dotenv(env_file)


load_env()


def handle_list(_):
    pydoc.pager('\n'.join('Hello World %d!' % x for x in range(200)))  # TODO implement using texttable
    print("Not implemented")


class TextInputFields(str, Enum):
    invoice_number = 'rechnung-nr'
    client_identifier = 'client'
    ort = 'ort'
    leistungsdatum = 'leistungsdatum'
    tatigkeit = 'tätigkeit'
    nettobetrag = 'nettobetrag'


class Client:
    def __init__(self, identifier: str, vat: Decimal, address_name: str, address_street: str, address_city: str,
                 email: str):
        self.identifier = identifier
        self.vat = vat
        self.address_name = address_name
        self.address_street = address_street
        self.address_city = address_city
        self.email = email


class Invoice:
    def __init__(self, invoice_number: str, client_identifier: str, ort: str, leistungsdatum: str, tatigkeit: str,
                 nettobetrag: Decimal, files: list):
        self.invoice_number = invoice_number
        self.client_identifier = client_identifier
        self.ort = ort
        self.leistungsdatum = leistungsdatum
        self.tatigkeit = tatigkeit
        self.nettobetrag = nettobetrag
        self.files = files


def extract_text_fields(email_body: str) -> Dict[TextInputFields, Any]:
    fields: Dict[TextInputFields, Any] = {}
    errors = []

    lines = email_body.splitlines()
    for line_index, line in enumerate(lines):
        line_number = line_index + 1
        tokens = line.split(" ", 1)
        if len(tokens) < 2:
            errors.append(f"Line {line_number} doesn't have space separation: {line}")
            continue

        field_name = tokens[0]
        field_value = tokens[1]
        field_enum: TextInputFields
        try:
            field_enum = TextInputFields(field_name)
        except ValueError:
            errors.append(f"Line {line_number} doesn't have field '{field_name}': {line}")
            continue

        if field_enum in fields.keys():
            errors.append(f"Line {line_number}'s field '{field_name}' was already encountered: {line}")
            continue

        fields[field_enum] = field_value

    if len(errors) > 0:
        raise Exception("\n".join(errors))

    return fields


def get_invoice_data_from_email(email_id: str) -> Invoice:
    pass  # TODO


def handle_add(email_id: str):
    # TODO:
    #   get_invoice_data_from_email
    #       get email by id
    #   get_client(client_identifier: str) -> dynamic reading of the clients sheet
    #   compute vat and Rechnungsbetrag
    #   docx and pdf generation
    #   create draft
    pass
    print(get_clients_file())


def get_clients_file():
    url = os.environ.get("CLIENTS_SHEET_URL")
    response = requests.get(url)

    if not response.ok:
        print(response.text)
        raise Exception(response.status_code)

    clients_file = os.path.join(tempfile.gettempdir(), "clients.csv")
    with open(clients_file, "wb") as f:
        f.write(response.content)

    return clients_file


def main():
    descr = "Program to list received rechnung emails or to create rechnung email draft based on one of those emails"
    parser = argparse.ArgumentParser(description=descr)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List the emails")
    list_parser.set_defaults(func=handle_list)

    # add command
    add_parser = subparsers.add_parser("add", help="Create rechnung email draft based on an email_id")
    add_parser.add_argument("email_id", help="Email ID for the input rechnung data")
    add_parser.set_defaults(func=lambda handler_args: handle_add(handler_args.email_id))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
