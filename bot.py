# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from commands.nfl_commands import setup as setup_nfl

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        print(f'Connected to: {guild.name} (id: {guild.id})')

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command not found! Try `!help` for available commands.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"❌ An error occurred: {error}")

async def setup_commands():
    """Load all command modules"""
    await setup_nfl(bot)

async def main():
    await setup_commands()
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())