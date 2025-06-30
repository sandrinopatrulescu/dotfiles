#!/usr/bin/env python3
import argparse
import email
import imaplib
import os
import pydoc
import tempfile
from decimal import Decimal
from email.header import decode_header
from email.utils import parseaddr
from email.utils import parsedate_to_datetime
from enum import Enum
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from texttable import Texttable


def load_env():
    env_file = os.path.expandvars(os.environ.get("ALEX_RECHNUNG_ENV_FILE"))
    load_dotenv(env_file)


def get_imap_connection():
    email_address = os.getenv("INPUT_EMAIL_ADDRESS")
    app_password = os.getenv("INPUT_EMAIL_APP_PASSWORD")
    imap_server = os.getenv("INPUT_EMAIL_IMAP_SERVER")

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, app_password)
    mail.select("rechnungs", readonly=True)

    return mail


def handle_list(_):
    mail = get_imap_connection()
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    table = Texttable(max_width=200)
    table.header(["ID", "Date", "From", "Subject", "Body", "Attachments"])

    emails_shown = 5
    for email_id in list(reversed(email_ids))[:emails_shown]:
        print(email_id, end=' ')
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        from_email_address = parseaddr(msg["From"])[0]
        dt_utc = parsedate_to_datetime(msg["Date"])
        local_dt = dt_utc.astimezone()

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        attachments = []
        for part in msg.walk():
            # Skip if not an attachment
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)

        row = [email_id, str(local_dt), from_email_address, subject, body, ';'.join(attachments)]
        table.add_row(row)

    print()
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
    load_env()

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
