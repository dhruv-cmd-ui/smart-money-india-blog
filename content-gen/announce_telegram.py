"""Announces the newest blog article on the Telegram channel (replaces the Make.com RSS -> Telegram scenario)."""
import argparse
import html
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

MANIFEST_PATH = Path(__file__).resolve().parent.parent / "docs" / "manifest.json"


def build_message(entry: dict) -> str:
    return (
        f"<b>New article: {html.escape(entry['title'], quote=False)}</b>\n\n"
        f"{html.escape(entry['description'], quote=False)}\n\n"
        f"Read it here: {entry['url']}\n\n"
        "#SmartInvestingIndia #PersonalFinance"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entry = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))[0]
    message = build_message(entry)
    print(message)
    if args.dry_run:
        print("Dry run — not sending.")
        return

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHANNEL_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHANNEL_ID not set — skipping announcement.")
        return

    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode()
    with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data=data, timeout=30) as resp:
        payload = json.loads(resp.read())
    if not payload.get("ok"):
        print(f"Telegram API error: {payload}")
        sys.exit(1)
    print("Announced on Telegram.")


if __name__ == "__main__":
    main()
