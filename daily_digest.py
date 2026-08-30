import os
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

import gspread
from google.oauth2.service_account import Credentials

# How many days ahead counts as "upcoming" for recurring tasks not yet due
UPCOMING_DAYS = 2

# --- Connect to Google Sheets ---
scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
gc = gspread.authorize(creds)

sheet_id = os.environ["SHEET_ID"]
print(f"DEBUG - Sheet ID length: {len(sheet_id)}, repr: {repr(sheet_id)}")
spreadsheet = gc.open_by_key(sheet_id)


def find_header_row(values, header_name="Task"):
    """Find the row index (0-based) where the real column headers live."""
    for i, row in enumerate(values):
        if row and row[0].strip() == header_name:
            return i
    return None


def get_unfinished_tasks(sheet_name):
    """Return (task, notes) tuples from a Daily/Weekly-style sheet where Done isn't checked."""
    ws = spreadsheet.worksheet(sheet_name)
    values = ws.get_all_values()
    header_idx = find_header_row(values)
    if header_idx is None:
        return []

    tasks = []
    for row in values[header_idx + 1:]:
        if not row or not row[0].strip():
            continue
        task = row[0].strip()
        done = row[1].strip().upper() if len(row) > 1 else ""
        notes = row[2].strip() if len(row) > 2 else ""
        if done != "TRUE":
            tasks.append((task, notes))
    return tasks


def get_due_and_upcoming_recurring():
    """Return (due_tasks, upcoming_tasks) as (task, notes) tuples from the Recurring sheet,
    using the sheet's own Status column."""
    ws = spreadsheet.worksheet("Recurring")
    values = ws.get_all_values()
    header_idx = find_header_row(values)
    if header_idx is None:
        return [], []

    due, upcoming = [], []

    for row in values[header_idx + 1:]:
        if not row or not row[0].strip():
            continue
        task = row[0].strip()
        status = row[4].strip() if len(row) > 4 else ""
        notes = row[5].strip() if len(row) > 5 else ""

        if status.lower() == "due":
            due.append((task, notes))
        elif status.lower() == "upcoming":
            upcoming.append((task, notes))

    return due, upcoming

def format_task_lines(tasks):
    lines = []
    for task, notes in tasks:
        lines.append(f"- {task}")
        if notes:
            lines.append(f"    note: {notes}")
    return lines

def build_email_body():
    daily = get_unfinished_tasks("Daily")
    weekly = get_unfinished_tasks("Weekly")
    due, upcoming = get_due_and_upcoming_recurring()

    lines = []

    lines.append("DAILY TASKS")
    lines.extend(format_task_lines(daily)) if daily else lines.append("(none outstanding)")

    lines.append("")
    lines.append("WEEKLY TASKS")
    lines.extend(format_task_lines(weekly)) if weekly else lines.append("(none outstanding)")

    lines.append("")
    lines.append("RECURRING TASKS DUE NOW")
    lines.extend(format_task_lines(due)) if due else lines.append("(none due)")

    lines.append("")
    lines.append(f"UPCOMING (next {UPCOMING_DAYS} days)")
    lines.extend(format_task_lines(upcoming)) if upcoming else lines.append("(nothing upcoming)")

    lines.append("")
    lines.append("Spreadsheet link: https://docs.google.com/spreadsheets/d/1slp2D9KmRG810TrTFhP3yrth83IXY7yUaUrgsi8ewyQ/edit?usp=sharing")

    return "\n".join(lines)


def send_email(body):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    to_email = os.environ["TO_EMAIL"]

    msg = MIMEText(body)
    msg["Subject"] = f"Daily Task Digest - {datetime.now().strftime('%A %m/%d')}"
    msg["From"] = gmail_address
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_email], msg.as_string())


if __name__ == "__main__":
    body = build_email_body()
    print(body)  # so it also shows up in the GitHub Actions log for debugging
    send_email(body)
