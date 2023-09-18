import os
import logging
import asyncio
import sqlite3
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_ID = os.getenv("STINE_API_ID")
API_HASH = os.getenv("STINE_API_HASH")
API_TOKEN = os.getenv("STINE_API_TOKEN")

# Initialize Telethon client
client = TelegramClient('anon', API_ID, API_HASH)

# Initialize counters
user_joined_count = 0
user_added_count = 0
message_count = 0

# Database Class
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot_stats.db')
        self.cursor = self.conn.cursor()
        self.initialize()

    def initialize(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stats
                              (id INTEGER PRIMARY KEY, user_joined_count INTEGER, user_added_count INTEGER, message_count INTEGER)''')
        self.conn.commit()

    def write_stats(self, user_joined_count, user_added_count, message_count):
        self.cursor.execute('INSERT OR REPLACE INTO stats (id, user_joined_count, user_added_count, message_count) VALUES (1, ?, ?, ?)',
                            (user_joined_count, user_added_count, message_count))
        self.conn.commit()

# Initialize Database
db = Database()

@client.on(events.ChatAction(chats='@stine_ca'))
async def handler(event):
    global user_joined_count, user_added_count, message_count
    try:
        username = event.user.username or event.user.first_name
        formatted_username = f"`@{username}`"
        if event.user_joined or event.user_added:
            if event.user_joined:
                user_joined_count += 1
            if event.user_added:
                user_added_count += 1
            await event.reply(f"{formatted_username} `is no longer a spectator.`")
            db.write_stats(user_joined_count, user_added_count, message_count)
        elif event.user_left or event.user_kicked:
            await event.reply(f"{formatted_username} `is a spectator again.`")
    except Exception as e:
        logger.error(f"An error occurred in handler: {e}, type: {type(e)}")

@client.on(events.NewMessage(chats='@stine_ca'))
async def new_message_handler(event):
    global message_count
    message_count += 1
    db.write_stats(user_joined_count, user_added_count, message_count)
    logger.info(f"Total messages: {message_count}")

@client.on(events.NewMessage(pattern='/about'))
async def about(event):
    await event.reply("Join us on an exhilarating journey through the ever-evolving landscape of independent-collaborative creation, shaping a new era of media innovation.\nCheck back soon!")

@client.on(events.NewMessage(pattern='/shortcuts'))
async def shortcuts(event):
    await event.reply("—𝑺𝓱𝒐𝒓𝒕𝒄𝒖𝒕𝒔—\n"
                      "x.com/ryanjvi 𝕏\n"
                      "t.me/ryanonx Ⓡ𝖿𝖾𝖾𝖽\n"
                      "gitlab.com/wuk 𝔤𝔦𝔱\n"
                      "stine.ca/feed Ⓡ𐌔𐌔\n"
                      "t.me/ryanjvi 𝗣𝗠")

async def main_loop():
    while True:
        try:
            await client.start(bot_token=API_TOKEN)
            await client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Bot encountered an error: {e}, type: {type(e)}")
            logger.info("Restarting bot in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main_loop())
