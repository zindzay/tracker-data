#!/usr/bin/env python3
"""Send a message to a Telegram chat using only the standard library."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_env_file(path):
    if not os.path.isfile(path):
        return {}

    values = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            values[key] = value
    return values


def get_config():
    file_values = load_env_file(ENV_PATH)
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or file_values.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or file_values.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        sys.exit(
            "Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set "
            "in the environment or in a .env file next to this script."
        )

    return token, chat_id


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        sys.exit(f"Telegram API error: {body.get('description', body)}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e.reason}")

    if not body.get("ok"):
        sys.exit(f"Telegram API error: {body}")

    return body


def main():
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()

    if not text:
        sys.exit("Usage: send.py <message text> (or pipe text via stdin)")

    token, chat_id = get_config()
    send_message(token, chat_id, text)
    print("Message sent.")


if __name__ == "__main__":
    main()
