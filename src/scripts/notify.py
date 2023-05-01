# for notification

# Standard Library
import argparse
import asyncio
import os

# Third Party Library
import aiohttp
from discord import Webhook
from dotenv import load_dotenv


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", required=True, help="message")

    args = parser.parse_args()

    return args


async def notify_discord(webhook_url, message):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(message, username="HPO")


if __name__ == "__main__":
    load_dotenv()

    args = get_args()

    MESSAGE = args.m

    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    asyncio.run(notify_discord(webhook_url=webhook_url, message=MESSAGE))
