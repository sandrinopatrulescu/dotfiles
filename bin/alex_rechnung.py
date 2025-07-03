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

DEFAULT_LIST_SIZE = 5


def load_env():
    env_file = os.path.expandvars(os.environ.get("ALEX_RECHNUNG_ENV_FILE"))
    load_dotenv(env_file)


def get_imap_connection():
    email_address = os.getenv("INPUT_EMAIL_ADDRESS")
    app_password = os.getenv("INPUT_EMAIL_APP_PASSWORD")
    imap_server = os.getenv("INPUT_EMAIL_IMAP_SERVER")

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, app_password)
    mail.select("rechnungen", readonly=True)

    return mail


def get_email_by_id(mail, email_id: str):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status == "OK":
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        return msg
    else:
        print(f"Failed to get email by id: {email_id}. Status: {status}")
        raise Exception(msg_data)


def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                charset = part.get_content_charset() or part.get_charset() or "utf-8"
                try:
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break
    else:
        charset = msg.get_content_charset() or msg.get_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")

    return body


def get_email_data(msg):
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")

    sender = parseaddr(msg["From"])[0]

    dt_utc = parsedate_to_datetime(msg["Date"])
    local_dt = dt_utc.astimezone()

    body = extract_email_body(msg)

    attachments = []
    for part in msg.walk():
        # Skip if not an attachment
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                attachments.append(filename)

    return local_dt, sender, subject, body, attachments


def handle_list(emails_requested: int):
    mail = get_imap_connection()
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    emails_count = len(email_ids)
    emails_available = min(emails_requested, emails_count)
    emails_available_ids = list(reversed(email_ids))[:emails_available]
    print("emails found: ", emails_count)
    print(f"emails available: {emails_available} ids: {emails_available_ids}")

    table = Texttable(max_width=200)
    table.header(["ID", "Date", "From", "Subject", "Body", "Attachments"])

    for email_index, email_id in enumerate(emails_available_ids):
        print(f"Obtaining email {email_index + 1}/{emails_available} with id {email_id}...")
        msg = get_email_by_id(mail, email_id)
        local_dt, sender, subject, body, attachments = get_email_data(msg)
        row = [email_id, local_dt, sender, subject, body, attachments]
        table.add_row(row)

    mail.close()
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
    main()
