#!/usr/bin/env python3
import imaplib
import os
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- Configuration ---
EMAIL = os.getenv('OTHERS_M_EMAIL_ADDRESS')
APP_PASSWORD = os.getenv('OTHERS_M_EMAIL_APP_PASSWORD')
IMAP_SERVER = os.getenv('OTHERS_M_EMAIL_IMAP_SERVER')
IMAP_PORT = int(os.getenv('OTHERS_M_EMAIL_IMAP_PORT'))

# --- Create the draft message ---
msg = MIMEMultipart()
msg["Subject"] = f"Draft Subject {datetime.now().isoformat()}"
msg["From"] = EMAIL
msg["To"] = "recipient@example.com"

body = f"This is the body of the draft email.\n{os.uname()}"
msg.attach(MIMEText(body, "plain"))

raw_message = msg.as_bytes()

# --- Connect to email service via IMAP ---
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(EMAIL, APP_PASSWORD)

status, folders = mail.list()
for folder in folders:
    print(folder.decode())

while True:
    if input("Send email? Write 'ok' to continue: ") == "ok":
        break

# Select the Drafts folder
mailbox = '"Draft"'
mail.select(mailbox)

# Append the message to the Drafts folder
now = datetime.now(timezone.utc)
result = mail.append(mailbox, '', imaplib.Time2Internaldate(now), raw_message)
print(result)
print("✅ Draft created successfully.")

# Logout
logout_result = mail.logout()
print('logout_result=', logout_result)
