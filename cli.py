#!/usr/bin/env python3
"""
Telegram CLI — thin wrapper over Telethon for OpenClaw agent exec calls.
Usage:
    python3 cli.py chats [--limit N]
    python3 cli.py read <chat_id> [--limit N]
    python3 cli.py send <chat_id> <text>
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

# Load .env from script directory
load_dotenv(Path(__file__).parent / ".env")

API_ID = int(os.environ["TELEGRAM_API_ID"])
API_HASH = os.environ["TELEGRAM_API_HASH"]
SESSION_STRING = os.environ.get("TELEGRAM_SESSION_STRING", "")
SESSION_NAME = os.environ.get("TELEGRAM_SESSION_NAME", "telegram_session")


def make_client():
    if SESSION_STRING:
        return TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    return TelegramClient(SESSION_NAME, API_ID, API_HASH)


def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


async def cmd_chats(limit=20):
    client = make_client()
    await client.connect()
    dialogs = await client.get_dialogs(limit=limit)
    result = []
    for d in dialogs:
        result.append({
            "id": d.entity.id,
            "name": d.name,
            "type": d.entity.__class__.__name__,
            "unread": d.unread_count,
        })
    await client.disconnect()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=json_serial))


async def cmd_read(chat_id, limit=20):
    client = make_client()
    await client.connect()
    entity = await client.get_entity(int(chat_id))
    messages = await client.get_messages(entity, limit=limit)
    result = []
    for m in messages:
        sender_name = ""
        if m.sender:
            sender_name = getattr(m.sender, "first_name", "") or getattr(m.sender, "title", "") or ""
        result.append({
            "id": m.id,
            "date": m.date.isoformat() if m.date else None,
            "sender": sender_name,
            "sender_id": m.sender_id,
            "text": m.text or "",
        })
    await client.disconnect()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=json_serial))


async def cmd_send(chat_id, text):
    client = make_client()
    await client.connect()
    entity = await client.get_entity(int(chat_id))
    msg = await client.send_message(entity, text)
    await client.disconnect()
    print(json.dumps({"ok": True, "message_id": msg.id}, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "chats":
        limit = 20
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        asyncio.run(cmd_chats(limit))

    elif cmd == "read":
        if len(sys.argv) < 3:
            print("Usage: cli.py read <chat_id> [--limit N]")
            sys.exit(1)
        chat_id = sys.argv[2]
        limit = 20
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            limit = int(sys.argv[idx + 1])
        asyncio.run(cmd_read(chat_id, limit))

    elif cmd == "send":
        if len(sys.argv) < 4:
            print("Usage: cli.py send <chat_id> <text>")
            sys.exit(1)
        chat_id = sys.argv[2]
        text = " ".join(sys.argv[3:])
        asyncio.run(cmd_send(chat_id, text))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
