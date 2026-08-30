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
spreadsheet = gc.open_by_key(sheet_id)


def find_header_row(values, header_name="Task"):
    """Find the row index (0-based) where the real column headers live."""
    for i, row in enumerate(values):
        if row and row[0].strip() == header_name:
            return i
    return None


def get_unfinished_tasks(sheet_name):
    """Return task names from a Daily/Weekly-style sheet where Done isn't checked."""
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
        if done != "TRUE":
            tasks.append(task)
    return tasks


def get_due_and_upcoming_recurring():
    """Return (due_tasks, upcoming_tasks) from the Recurring sheet."""
    ws = spreadsheet.worksheet("Recurring")
    values = ws.get_all_values()
    header_idx = find_header_row(values)
    if header_idx is None:
        return [], []

    today = datetime.now().date()
    due, upcoming = [], []

    for row in values[header_idx + 1:]:
        if not row or not row[0].strip():
            continue
        task = row[0].strip()
        next_due_str = row[3].strip() if len(row) > 3 else ""
        status = row[4].strip() if len(row) > 4 else ""

        if status.lower() == "due":
            due.append(task)
        elif next_due_str:
            try:
                next_due = datetime.strptime(next_due_str, "%m/%d/%Y").date()
            except ValueError:
                continue
            days_away = (next_due - today).days
            if 0 <= days_away <= UPCOMING_DAYS:
                upcoming.append(f"{task} (due {next_due.strftime('%a %-m/%-d')})")

    return due, upcoming


def build_email_body():
    daily = get_unfinished_tasks("Daily")
    weekly = get_unfinished_tasks("Weekly")
    due, upcoming = get_due_and_upcoming_recurring()

    lines = []

    lines.append("DAILY TASKS")
    lines.extend(f"- {t}" for t in daily) if daily else lines.append("(none outstanding)")

    lines.append("")
    lines.append("WEEKLY TASKS")
    lines.extend(f"- {t}" for t in weekly) if weekly else lines.append("(none outstanding)")

    lines.append("")
    lines.append("RECURRING TASKS DUE NOW")
    lines.extend(f"- {t}" for t in due) if due else lines.append("(none due)")

    lines.append("")
    lines.append(f"UPCOMING (next {UPCOMING_DAYS} days)")
    lines.extend(f"- {t}" for t in upcoming) if upcoming else lines.append("(nothing upcoming)")

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
