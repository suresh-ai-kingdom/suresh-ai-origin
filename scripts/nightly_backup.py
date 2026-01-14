#!/usr/bin/env python3
"""Nightly backup with integrity check and alerts."""

import os
import sqlite3
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

from backup_db import create_backup, cleanup_old_backups, get_db_path

PROD_NAME = os.getenv("PROJECT_NAME", "SURESH AI ORIGIN")
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "suresh.ai.origin@outlook.com")
EMAIL_USER = os.getenv("EMAIL_USER", "suresh.ai.origin@outlook.com")
EMAIL_PASS = os.getenv("EMAIL_PASS")
BACKUP_KEEP = int(os.getenv("BACKUP_KEEP", "7"))
NOTIFY_SUCCESS = os.getenv("BACKUP_NOTIFY_SUCCESS", "false").lower() == "true"


def integrity_check(db_path: str) -> tuple[bool, str]:
    """Run SQLite integrity check on the given database file."""
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("PRAGMA integrity_check;").fetchone()
        result = (row[0] if row else "no result").lower()
        return result == "ok", row[0] if row else "no result"
    finally:
        conn.close()


def send_webhook(subject: str, message: str) -> None:
    if not ALERT_WEBHOOK:
        return
    payload = {"text": f"💾 {PROD_NAME}: {subject}\n{message}"}
    try:
        requests.post(ALERT_WEBHOOK, json=payload, timeout=5)
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  Webhook send failed: {exc}")


def send_email(subject: str, message: str) -> None:
    if not EMAIL_PASS:
        return
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ALERT_EMAIL
    msg["Subject"] = f"{PROD_NAME} backup: {subject}"
    msg.attach(MIMEText(message, "plain"))
    try:
        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  Email send failed: {exc}")


def notify(subject: str, message: str, include_success: bool = False) -> None:
    if include_success or subject.lower().startswith("fail") or subject.lower().startswith("error"):
        send_webhook(subject, message)
        send_email(subject, message)


def run_once() -> int:
    started = time.time()
    try:
        backup_path = create_backup(get_db_path())
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        ok, integrity_msg = integrity_check(str(backup_path))

        cleanup_old_backups(keep_count=BACKUP_KEEP)

        duration = time.time() - started
        status_line = (
            f"Backup {backup_path.name} ({size_mb:.2f} MB) in {duration:.1f}s | integrity: {integrity_msg}"
        )
        print(status_line)

        if ok:
            notify("success", status_line, include_success=NOTIFY_SUCCESS)
            return 0

        notify("fail", f"Integrity check failed: {status_line}")
        return 1
    except Exception as exc:  # noqa: BLE001
        notify("error", f"Backup run crashed: {exc}")
        print(f"❌ Backup run crashed: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(run_once())
