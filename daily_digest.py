import os
import json
import re
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import gspread
from google.oauth2.service_account import Credentials

UPCOMING_DAYS = 2

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
gc = gspread.authorize(creds)

sheet_id = os.environ["SHEET_ID"]
spreadsheet = gc.open_by_key(sheet_id)

URL_PATTERN = re.compile(r'(https?://\S+)')


def linkify(text):
    """Turn any raw URL in a string into a clickable HTML link."""
    if not text:
        return ""

    def replace(match):
        url = match.group(1)
        label = "View sheet" if "docs.google.com/spreadsheets" in url else "Link"
        return f'<a href="{url}" style="color:#4A7CFE;text-decoration:none;">{label}</a>'

    return URL_PATTERN.sub(replace, text)


def find_header_row(values, header_name="Task"):
    for i, row in enumerate(values):
        if row and row[0].strip() == header_name:
            return i
    return None


def get_unfinished_tasks(sheet_name):
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


def render_section(title, tasks, accent_color, empty_message):
    """Build one styled HTML block for a section (Daily, Weekly, etc)."""
    html = f'''
    <div style="margin-bottom:28px;">
      <div style="font-size:15px;font-weight:700;color:{accent_color};
                  text-transform:uppercase;letter-spacing:0.5px;
                  border-bottom:2px solid {accent_color};padding-bottom:6px;margin-bottom:12px;">
        {title}
      </div>
    '''
    if not tasks:
        html += f'<div style="color:#999;font-style:italic;padding:4px 0;">{empty_message}</div>'
    else:
        for task, notes in tasks:
            html += f'''
            <div style="padding:8px 0;border-bottom:1px solid #f0f0f0;">
              <div style="font-size:14px;color:#222;">{task}</div>
            '''
            if notes:
                html += f'<div style="font-size:12px;color:#777;margin-top:2px;">{linkify(notes)}</div>'
            html += '</div>'
    html += '</div>'
    return html


def build_email_html():
    daily = get_unfinished_tasks("Daily")
    weekly = get_unfinished_tasks("Weekly")
    due, upcoming = get_due_and_upcoming_recurring()
    today_str = datetime.now().strftime("%A, %B %-d")

    html = f'''
    <html>
    <body style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;
                 background-color:#f7f7f8;padding:24px;margin:0;">
      <div style="max-width:520px;margin:0 auto;background:#ffffff;
                  border-radius:12px;padding:28px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
        <div style="font-size:20px;font-weight:700;color:#111;margin-bottom:4px;">
          Daily Digest
        </div>
        <div style="font-size:13px;color:#999;margin-bottom:24px;">
          {today_str}
        </div>

        {render_section("Daily Tasks", daily, "#4A7CFE", "Nothing outstanding — nice work.")}
        {render_section("Weekly Tasks", weekly, "#8A4AFE", "Nothing outstanding.")}
        {render_section("Due Now", due, "#FE4A4A", "Nothing due today.")}
        {render_section(f"Upcoming ({UPCOMING_DAYS} days)", upcoming, "#FEA34A", "Nothing upcoming.")}

        <div style="margin-top:20px;padding-top:16px;border-top:1px solid #eee;
                    font-size:12px;color:#aaa;">
          <a href="https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
             style="color:#4A7CFE;text-decoration:none;">Open full spreadsheet →</a>
        </div>
      </div>
    </body>
    </html>
    '''
    return html


def send_email(html_body):
    gmail_address = os.environ["GMAIL_ADDRESS"]
    gmail_app_password = os.environ["GMAIL_APP_PASSWORD"]
    to_email = os.environ["TO_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Task Digest — {datetime.now().strftime('%A %m/%d')}"
    msg["From"] = gmail_address
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_app_password)
        server.sendmail(gmail_address, [to_email], msg.as_string())


if __name__ == "__main__":
    html_body = build_email_html()
    send_email(html_body)
