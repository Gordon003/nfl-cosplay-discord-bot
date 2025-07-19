# bot.py
import os

import discord
from dotenv import load_dotenv

from utils import read_csv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=discord.Intents.default())

# setting up the bot
teams_info = read_csv.get_teams_info()
teams_character = read_csv.get_teams_character()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        print(f'Connected to: {guild.name} (id: {guild.id})')

client.run(TOKEN)