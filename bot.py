# bot.py
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import requests
import base64

SERVER_URL = 'http://localhost:5900'

TEST_GUILD_ID = 445779215791554571
DBAPO_GUILD_ID = 173308004936974337

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

@tree.command(
        name="aram-player-stats",
        description="Replies with ARAM player stats for a given game name and tagline (e.g. hsaito NA1)",
        guilds=[discord.Object(id=DBAPO_GUILD_ID), discord.Object(id=TEST_GUILD_ID)]

)
async def get_player_stats(interaction, game_name: str, tag_line: str):
    r = requests.get(f'{SERVER_URL}/graphics/player-stats/{game_name}/{tag_line}')
    imgdata = base64.b64decode(r.text)
    filename = 'aram-stats.png'
    with open(filename, 'wb') as f:
      f.write(imgdata)
    await interaction.response.send_message("Here are your ARAM stats!", file=discord.File(filename))



@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=TEST_GUILD_ID))
    await tree.sync(guild=discord.Object(id=DBAPO_GUILD_ID))
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)


