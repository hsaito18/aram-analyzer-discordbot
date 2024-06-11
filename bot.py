# bot.py
import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from typing import List
import asyncio
import requests
import base64

SERVER_URL = "http://localhost:5900"

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

working = False


def run(guild_ids: List[discord.Object]):
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    tree = app_commands.CommandTree(client)

    @tree.command(
        name="aram-player-stats",
        description="Replies with ARAM player stats for a given game name and tagline (e.g. hsaito NA1)",
        guilds=guild_ids,
    )
    async def get_player_stats(interaction, game_name: str, tag_line: str):
        global working
        await interaction.response.defer()
        while working:
            await asyncio.sleep(0.5)
        working = True

        save_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/save-matches",
            data={"gameName": game_name, "tagLine": tag_line},
        )
        analyze_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/analyze-matches",
            data={"gameName": game_name, "tagLine": tag_line},
        )
        if analyze_matches.status_code != 200 or save_matches.status_code != 200:
            await interaction.followup.send(
                "There was a problem updating your matches."
            )
            working = False
            return
        r = requests.get(f"{SERVER_URL}/graphics/player-stats/{game_name}/{tag_line}")
        imgdata = base64.b64decode(r.text)
        filename = f"aram-stats.png"
        print(filename)
        with open(filename, "wb") as f:
            f.write(imgdata)
        await interaction.followup.send(
            "Here are your ARAM stats!", file=discord.File(filename)
        )
        working = False

    @client.event
    async def on_ready():
        for guild_id in guild_ids:
            await tree.sync(guild=guild_id)
        print(f"{client.user} has connected to Discord!")

    client.run(TOKEN)
