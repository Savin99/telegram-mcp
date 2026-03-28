import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def main():
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.start()
    session_string = client.session.save()
    print(f"\n\nYour new session string:\n{session_string}\n")
    await client.disconnect()

asyncio.run(main())
