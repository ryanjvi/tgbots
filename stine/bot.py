from telethon import TelegramClient, events
import os
import logging
from dotenv import load_dotenv
import asyncio

# Initialize counters
user_joined_count = 0
user_added_count = 0
message_count = 0

# Function to write stats to a file
def write_stats_to_file():
    with open('stats.txt', 'w') as f:
        f.write(f"User Joined Count: {user_joined_count}\n")
        f.write(f"User Added Count: {user_added_count}\n")
        f.write(f"Total Messages: {message_count}\n")

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
API_TOKEN = os.getenv("API_TOKEN")

# Initialize Telethon client
client = TelegramClient('anon', API_ID, API_HASH)

# Listen for chat actions in a specific channel
@client.on(events.ChatAction(chats='@stine_ca'))
async def handler(event):
    global user_joined_count, user_added_count
    try:
        if event.user_joined:
            user_joined_count += 1
        if event.user_added:
            user_added_count += 1
        write_stats_to_file()  # Write stats after each update

        username = event.user.username if event.user.username else event.user.first_name
        await event.reply(f'@{username} is no longer a spectator.')
    except Exception as e:
        logger.error(f"An error occurred in handler: {e}")

@client.on(events.NewMessage(chats='@stine_ca'))
async def new_message_handler(event):
    global message_count
    message_count += 1
    write_stats_to_file()  # Write stats after each update
    logger.info(f"Total messages: {message_count}")
        
# Admin command /about
@client.on(events.NewMessage(pattern='/about'))
async def about(event):
    await event.reply("Join us on an exhilarating journey through the ever-evolving landscape of independent-collaborative creation, shaping a new era of media innovation.\nCheck back soon!")

# Admin command /shortcuts
@client.on(events.NewMessage(pattern='/shortcuts'))
async def shortcuts(event):
    await event.reply(
        "—𝑺𝓱𝒐𝒓𝒕𝒄𝒖𝒕𝒔—\n"
        "x.com/ryanjvi 𝕏\n"
        "t.me/ryanonx Ⓡ𝖿𝖾𝖾𝖽\n"
        "gitlab.com/wuk 𝔤𝔦𝔱\n"
        "stine.ca/feed Ⓡ𐌔𐌔\n"
        "t.me/ryanjvi 𝗣𝗠"
    )

# Start the Telethon client
async def main():
    await client.start(bot_token=API_TOKEN)
    await client.run_until_disconnected()

if __name__ == '__main__':
    while True:
        try:
            client.loop.run_until_complete(main())
        except Exception as e:
            logger.error(f"Bot encountered an error: {e}")
            logger.info("Restarting bot in 5 seconds...")
            asyncio.sleep(5)
