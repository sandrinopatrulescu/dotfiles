#!/usr/bin/env python3
import argparse
import email
import imaplib
import os
import pydoc
import quopri
import re
import tempfile
from datetime import datetime
from decimal import Decimal
from email.header import decode_header
from email.utils import parseaddr
from email.utils import parsedate_to_datetime
from enum import Enum
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from texttable import Texttable

DEFAULT_LIST_SIZE = 5

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
script_name = os.path.basename(__file__)
files_directory = os.path.join(tempfile.gettempdir(), script_name, timestamp)

print(f"Using directory: {files_directory}")


def load_env():
    env_file = os.path.expandvars(os.environ.get("ALEX_RECHNUNG_ENV_FILE"))
    load_dotenv(env_file)


def get_imap_client():
    email_address = os.getenv("INPUT_EMAIL_ADDRESS")
    app_password = os.getenv("INPUT_EMAIL_APP_PASSWORD")
    imap_server = os.getenv("INPUT_EMAIL_IMAP_SERVER")

    imap_client = imaplib.IMAP4_SSL(imap_server)
    imap_client.login(email_address, app_password)
    imap_client.select("rechnungen", readonly=True)

    return imap_client


def get_email_by_id(imap_client, email_id: str):
    status, msg_data = imap_client.fetch(email_id, "(RFC822)")
    if status == "OK":
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        return msg
    else:
        print(f"Failed to get email by id: {email_id}. Status: {status}")
        raise Exception(msg_data)


def decode_string(value: str):
    return quopri.decodestring(value).decode('utf-8')


def extract_text_from_html_part(part):
    html_encoded = part.get_payload()
    html = decode_string(html_encoded)
    bs = BeautifulSoup(html, "html.parser")
    string_list = list(bs.strings)

    cleaned_string_list = []
    for string in string_list:
        string_to_add = string
        if string == "\n":
            continue
        elif string.endswith('\xa0'):
            string_to_add = string_to_add[:-1]

        cleaned_string_list.append(string_to_add)

    return cleaned_string_list


def save_file(name: str, content: Any, directory: str):
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, name)
    with open(file_path, "wb") as file:
        file.write(content)

    return file_path


def extract_data_from_part(part, save_files: bool):
    content_type = part.get_content_type()

    if content_type in {'multipart/alternative', 'multipart/related', 'multipart/mixed'}:
        return 'none', []  # skipped
    elif content_type == "text/html":
        return 'html', extract_text_from_html_part(part)
    elif content_type == "text/plain":
        return 'text', []
    else:
        filename = part.get_filename()
        if filename is not None:
            file = filename
            if save_files:
                content = part.get_payload(decode=True)
                file = save_file(filename, content, files_directory)
            return 'file', file
        else:
            raise Exception(f"Unknown content type: {content_type}")


def extract_email_body_lines_and_files(msg, save_files: bool):
    type_to_data_list = {}
    parts = list(msg.walk()) if msg.is_multipart() else [msg]
    for part_index, part in enumerate(parts):
        data_type, data = extract_data_from_part(part, save_files)
        if data_type != 'none':
            data_list = type_to_data_list.setdefault(data_type, [])
            data_list.append(data)

    html_list = type_to_data_list.get('html', [])
    html_list_size = len(html_list)
    body_lines = []
    if html_list_size == 0:
        print("[WARN] no html data found")
        raise Exception("Text parsing not implemented")
        # text_list = type_to_data_list.get('text', [])
        # text_list_size = len(text_list)
        # if text_list_size == 0:
        #     raise Exception("No html nor text data found")
        # elif text_list_size > 0:
        #     body_lines = text_list[0]
        #     if text_list_size > 1:
        #         print("[WARN] text_list_size > 1")
    elif html_list_size > 0:
        body_lines = html_list[0]
        if html_list_size > 1:
            print("[WARN] html_list_size > 1")

    files = type_to_data_list.get('file', [])

    return body_lines, files


def get_email_data(imap_client, email_id, save_files: bool):
    msg = get_email_by_id(imap_client, email_id)

    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")

    sender_name_and_address = parseaddr(msg["From"])
    sender_address = sender_name_and_address[1]

    dt_utc = parsedate_to_datetime(msg["Date"])
    local_dt = dt_utc.astimezone()

    body, files = extract_email_body_lines_and_files(msg, save_files)

    return local_dt, sender_address, subject, body, files


def handle_list(emails_requested: int):
    imap_client = get_imap_client()
    status, messages = imap_client.search(None, "ALL")
    email_ids = messages[0].split()

    emails_count = len(email_ids)
    emails_available = min(emails_requested, emails_count)
    emails_available_ids = list(reversed(email_ids))[:emails_available]
    print("emails found: ", emails_count)
    print(f"emails available: {emails_available} ids: {emails_available_ids}")
    print()

    table = Texttable(max_width=200)
    table.header(["ID", "Date", "From", "Subject", "Body", "Attachments"])

    for email_index, email_id in enumerate(emails_available_ids):
        try:
            print(f"Obtaining email {email_index + 1}/{emails_available} with id {email_id}...", end='', flush=True)

            local_dt, sender, subject, body_lines, files_names = get_email_data(imap_client, email_id, False)

            print(f": {local_dt} | {sender} | {subject} | {body_lines} | {files_names}")

            row = [email_id, local_dt, sender, subject, '\n'.join(body_lines), files_names]
            table.add_row(row)
        finally:
            print()

    imap_client.close()
    pydoc.pager(table.draw())


class TextInputFields(str, Enum):
    invoice_number = 'rechnung-nr'
    client_identifier = 'client'
    ort = 'ort'
    leistungsdatum = 'leistungsdatum'
    tatigkeit = 'tätigkeit'
    nettobetrag = 'nettobetrag'


class Client:
    def __init__(self, identifier: str, vat: Decimal, address_name: str, address_street: str, address_city: str,
                 email_address: str):
        self.identifier = identifier
        self.vat = vat
        self.address_name = address_name
        self.address_street = address_street
        self.address_city = address_city
        self.email = email_address


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

        field_name = tokens[0].lower()
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


def number_string_to_decimal(value: str):
    if bool(re.search(r'[^0-9.,]', value)):
        raise Exception(f"Cannot convert {value} to a decimal. Reason: invalid characters")
    elif value.isdigit():
        parsed_value = value
    else:  # at least 1 separator exist
        dot_index = value.rfind('.')
        comma_index = value.rfind(',')

        has_two_separators = -1 not in {dot_index, comma_index}
        decimal_separator = '.' if dot_index > comma_index else ','

        if has_two_separators and decimal_separator == '.':
            raise Exception(f"Cannot convert {value} to a decimal. Reason: decimal separator must be ',' (comma)")
        else:
            parsed_value = value.replace('.', '').replace(',', '.')

    return Decimal(parsed_value)


def test_number_string_to_decimal():
    assert number_string_to_decimal('0') == Decimal('0')
    assert number_string_to_decimal('1') == Decimal('1')
    assert number_string_to_decimal('5') == Decimal('5')
    assert number_string_to_decimal('5,5') == Decimal('5.5')
    assert number_string_to_decimal('5,') == Decimal('5')
    assert number_string_to_decimal('1.066') == Decimal('1066')
    assert number_string_to_decimal('1066,50') == Decimal('1066.50')
    assert number_string_to_decimal('1.066,50') == Decimal('1066.50')
    assert number_string_to_decimal('1.234.567,89') == Decimal('1234567.89')


def email_data_to_invoice(text_fields, files_names):
    invoice_number = text_fields[TextInputFields.invoice_number]
    client_identifier = text_fields[TextInputFields.client_identifier]
    ort = text_fields[TextInputFields.ort]
    leistungsdatum = text_fields[TextInputFields.leistungsdatum]
    tatigkeit = text_fields[TextInputFields.tatigkeit]
    nettobetrag = number_string_to_decimal(text_fields[TextInputFields.nettobetrag])

    invoice = Invoice(invoice_number, client_identifier, ort, leistungsdatum, tatigkeit, nettobetrag, files_names)

    return invoice


def get_invoice_data_from_email(email_id: str) -> Invoice:
    imap_client = get_imap_client()
    _, _, _, body_lines, files_names = get_email_data(imap_client, email_id, True)
    text_fields = extract_text_fields("\n".join(body_lines))

    invoice = email_data_to_invoice(text_fields, files_names)
    return invoice


def handle_add(email_id: str):
    # TODO:
    #   get_client(client_identifier: str) -> dynamic reading of the clients sheet
    #   compute vat and Rechnungsbetrag
    #   docx and pdf generation
    #   create draft
    invoice = get_invoice_data_from_email(email_id)
    print(get_clients_file())
    print(list(map(lambda x: (x, getattr(invoice, x)), filter(lambda x: not x.startswith("__"), dir(invoice)))))


def get_clients_file():
    url = os.environ.get("CLIENTS_SHEET_URL")
    response = requests.get(url)

    if not response.ok:
        print(response.text)
        raise Exception(response.status_code)

    clients_file = os.path.join(files_directory, "clients.csv")
    with open(clients_file, "wb") as f:
        f.write(response.content)

    return clients_file


def main():
    load_env()

    descr = "Program to list received rechnung emails or to create rechnung email draft based on one of those emails"
    parser = argparse.ArgumentParser(description=descr)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List the emails")
    list_parser.add_argument(
        "-n", "--limit",
        type=int,
        default=DEFAULT_LIST_SIZE,
        help=f"Number of emails to list (default: {DEFAULT_LIST_SIZE})"
    )
    list_parser.set_defaults(func=handle_list)
    list_parser.set_defaults(func=lambda handler_args: handle_list(handler_args.limit))

    # add command
    add_parser = subparsers.add_parser("add", help="Create rechnung email draft based on an email_id")
    add_parser.add_argument("email_id", help="Email ID for the input rechnung data")
    add_parser.set_defaults(func=lambda handler_args: handle_add(handler_args.email_id))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    test_number_string_to_decimal()
    main()
