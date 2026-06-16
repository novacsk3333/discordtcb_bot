import json
import re

import discord
from discord.ext import commands, tasks
from playwright.async_api import async_playwright

CHANNEL_ID = #CHANNEL ID HERE

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


def load_data():
    try:
        with open("chapter_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "chapter": 1184,
            "id": 7987
        }


def save_data(chapter, chapter_id):
    with open("chapter_data.json", "w") as f:
        json.dump(
            {
                "chapter": chapter,
                "id": chapter_id
            },
            f
        )


@tasks.loop(minutes=30)
async def check_chapter():
    print("Checking chapter...")

    data = load_data()

    current_chap = data["chapter"]
    current_id = data["id"]

    print(f"Stored chapter: {current_chap}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.goto(
            "https://tcbonepiecechapters.com/mangas/5/one-piece",
            wait_until="networkidle"
        )

        text = await (
            page.locator("div.text-lg.font-bold")
            .first
            .inner_text()
        )

        print(f"Page text: {text}")

        await browser.close()

    match = re.search(r"Chapter\s+(\d+)", text)

    if match:
        latest_chap = int(match.group(1))

        print(f"Latest chapter: {latest_chap}")

        if latest_chap > current_chap:
            print("New chapter found!")

            latest_id = current_id + (latest_chap - current_chap)

            url = (
                f"https://tcbonepiecechapters.com/chapters/"
                f"{latest_id}/one-piece-chapter-{latest_chap}"
            )

            channel = bot.get_channel(CHANNEL_ID)

            print(f"Channel: {channel}")

            if channel:
                await channel.send(
                    f"🚨 New One Piece chapter!\n{url}"
                )

            save_data(latest_chap, latest_id)
        else:
            print("No new chapter.")
    else:
        print("Couldn't parse chapter number.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    if not check_chapter.is_running():
        check_chapter.start()


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


bot.run('INSERT TOKEN HERE)
