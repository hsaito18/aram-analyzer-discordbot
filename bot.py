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

if not isinstance(TOKEN, str):
    raise ValueError("TOKEN must be a string")

working = False


def match_time_formatter(time: float) -> str:
    minutes = int(time // 60)
    seconds = int(time % 60)
    return f"{minutes}:{seconds:02d}"


def run(guild_ids: List[discord.Object]):
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    tree = app_commands.CommandTree(client)

    @tree.command(
        name="aram-player-champ-stats",
        description="Champion stats for a given game name, tagline, and champion (e.g. hsaito NA1 Leblanc)",
        guilds=guild_ids,
    )
    async def get_champ_stats(interaction, game_name: str, tag_line: str, champ: str):
        global working
        await interaction.response.defer()
        while working:
            await asyncio.sleep(0.5)
        working = True

        save_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/save-matches",
            data={"gameName": game_name, "tagLine": tag_line},
        )
        if save_matches.status_code == 404:
            await interaction.followup.send(
                "Player has not been registered! Please use /aram-register to register player."
            )
            working = False
            return
        if save_matches.status_code == 429:
            await interaction.followup.send(
                "Server is busy with another request. Please try again in a few minutes."
            )
            working = False
            return
        analyze_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/analyze-matches",
            data={"gameName": game_name, "tagLine": tag_line},
        )
        if analyze_matches.status_code != 200 or save_matches.status_code != 200:
            await interaction.followup.send(
                f"There was a problem updating your matches. Error codes: SM:{save_matches.status_code}, AM:{analyze_matches.status_code}"
            )
            working = False
            return
        r = requests.get(
            f"{SERVER_URL}/graphics/champ-stats/{game_name}/{tag_line}/{champ}"
        )
        if r.status_code == 404:
            await interaction.followup.send(r.json)  # type: ignore
            working = False
            return
        imgdata = base64.b64decode(r.text)
        filename = f"aram-player-stats.png"
        with open(filename, "wb") as f:
            f.write(imgdata)
        await interaction.followup.send(
            f"Here are your ARAM stats for {champ}!", file=discord.File(filename)
        )
        working = False

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
        if save_matches.status_code == 404:
            await interaction.followup.send(
                "Player has not been registered! Please use /aram-register to register player."
            )
            working = False
            return
        if save_matches.status_code == 429:
            await interaction.followup.send(
                "Server is busy with another request. Please try again in a few minutes."
            )
            working = False
            return
        analyze_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/analyze-matches",
            data={"gameName": game_name, "tagLine": tag_line},
        )
        if analyze_matches.status_code != 200 or save_matches.status_code != 200:
            await interaction.followup.send(
                f"There was a problem updating your matches. Error codes: SM:{save_matches.status_code}, AM:{analyze_matches.status_code}"
            )
            working = False
            return
        r = requests.get(f"{SERVER_URL}/graphics/player-stats/{game_name}/{tag_line}")
        if r.status_code == 204:
            await interaction.followup.send("No ARAM games found for this player.")
            working = False
            return
        imgdata = base64.b64decode(r.text)
        filename = f"aram-stats.png"
        with open(filename, "wb") as f:
            f.write(imgdata)
        await interaction.followup.send(
            "Here are your ARAM stats!", file=discord.File(filename)
        )
        working = False

    @tree.command(
        name="aram-register",
        description="Registers a player for ARAM stats.",
        guilds=guild_ids,
    )
    async def register_player(interaction, game_name: str, tag_line: str):
        global working
        await interaction.response.defer()
        while working:
            await asyncio.sleep(0.5)
        working = True
        register = requests.post(
            f"{SERVER_URL}/players/register",
            data={"gameName": game_name, "tagLine": tag_line},
        )
        if register.status_code == 400:
            await interaction.followup.send(
                "Player has already been registered! Please use /aram-player-stats to get stats."
            )
            working = False
            return
        if register.status_code == 404:
            await interaction.followup.send(
                "Player not found! Please check your game name and tagline."
            )
            working = False
            return
        if register.status_code != 201:
            await interaction.followup.send(
                f"An error occurred while registering player. Error code: {register.status_code}"
            )
            working = False
            return
        await interaction.followup.send("Player registered successfully!")
        working = False

    @tree.command(
        name="aram-lineup-stats",
        description="Replies with winrate ARAM stats for a set of 5 players.",
        guilds=guild_ids,
    )
    async def get_lineup_stats(
        interaction,
        game_name1: str,
        tag_line1: str,
        game_name2: str,
        tag_line2: str,
        game_name3: str,
        tag_line3: str,
        game_name4: str,
        tag_line4: str,
        game_name5: str,
        tag_line5: str,
    ):
        global working
        await interaction.response.defer()
        while working:
            await asyncio.sleep(0.5)
        working = True
        save_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/save-matches",
            data={"gameName": game_name1, "tagLine": tag_line1},
        )
        if save_matches.status_code == 404:
            await interaction.followup.send("First player has not been found.")
            working = False
            return
        if save_matches.status_code == 429:
            await interaction.followup.send(
                "Server is busy with another request. Please try again in a few minutes."
            )
            working = False
            return
        analyze_matches: requests.Response = requests.post(
            f"{SERVER_URL}/players/analyze-matches",
            data={"gameName": game_name1, "tagLine": tag_line1},
        )
        if analyze_matches.status_code != 200 or save_matches.status_code != 200:
            await interaction.followup.send(
                f"There was a problem updating matches. Error codes: SM:{save_matches.status_code}, AM:{analyze_matches.status_code}"
            )
            working = False
            return
        lineup_data = requests.get(
            f"{SERVER_URL}/lineups/lineup/{game_name1}/{tag_line1}/{game_name2}/{tag_line2}/{game_name3}/{tag_line3}/{game_name4}/{tag_line4}/{game_name5}/{tag_line5}",
        )
        if lineup_data.status_code == 404:
            await interaction.followup.send(
                "Error getting one or more players. Please check your game names and taglines."
            )
            working = False
            return
        if lineup_data.status_code != 200:
            await interaction.followup.send(
                f"An error occurred while getting lineup. Error code: {lineup_data.status_code}"
            )
            working = False
            return
        data_obj = lineup_data.json()
        winrate = (
            data_obj["wins"] / (data_obj["wins"] + data_obj["losses"]) * 100
            if (data_obj["wins"] + data_obj["losses"] > 0)
            else 0
        )
        avg_game_time_string = match_time_formatter(data_obj["averageGameTime"])
        avg_win_time_string = match_time_formatter(data_obj["averageWinTime"])
        avg_loss_time_string = match_time_formatter(data_obj["averageLossTime"])
        kd_plus_minus_string = f"+{data_obj["kills"] - data_obj["deaths"]}" if data_obj["kills"] - data_obj["deaths"] > 0 else str(data_obj["kills"] - data_obj["deaths"])
        output = (
            f"{game_name1} | {game_name2} | {game_name3} | {game_name4} | {game_name5}\n"
            f"Record: {data_obj['wins']}-{data_obj['losses']}\nWinrate: {winrate:.1f}%\n"
            f"Average Game Time: {avg_game_time_string}  |  Average Win Time: {avg_win_time_string}  |  Average Loss Time: {avg_loss_time_string}\n"
            f"Kills: {data_obj['kills']}  |  Deaths: {data_obj['deaths']}  |  +/-: {kd_plus_minus_string}\n"
            f"Average Damage: {data_obj["averageDamage"]}  |  Average Damage Taken: {data_obj["averageDamageTaken"]}"
        )
        await interaction.followup.send(output)
        working = False

    @tree.command(
        name="aram-champion-stats",
        description="Replies with basic ARAM stats for a given champion.",
        guilds=guild_ids,
    )
    async def get_champion_stats(
        interaction,
        champ: str,
    ):
        global working
        await interaction.response.defer()
        while working:
            await asyncio.sleep(0.5)
        working = True
        champ_stats_res: requests.Response = requests.get(
            f"{SERVER_URL}/champions/{champ}"
        )
        if champ_stats_res.status_code == 404:
            await interaction.followup.send("Champion data not found.")
            working = False
            return
        if champ_stats_res.status_code != 200:
            await interaction.followup.send(
                f"An error occurred while getting champion data. Error code: {champ_stats_res.status_code}"
            )
            working = False
            return
        data_obj = champ_stats_res.json()
        overall = data_obj["overall"]
        output = (
            f"{champ} Stats \n"
            f"Record: {overall['wins']}-{overall['losses']}\nWinrate: {(overall['winRate']*100):.1f}%\n"
            f"KDA: {overall['kda']:.1f}"
        )
        await interaction.followup.send(output)
        working = False

    @client.event
    async def on_message(message):
        if client.user == None:
            return
        if client.user.mentioned_in(message):
            await message.channel.send("what do you want now")

    @client.event
    async def on_ready():
        for guild_id in guild_ids:
            await tree.sync(guild=guild_id)
        print(f"{client.user} has connected to Discord!")

    client.run(str(TOKEN))
