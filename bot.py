# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.data_manager import DataManager
import asyncio
from utils.api_cache import APICache
from utils.nfl_api import NFLAPIManager
from utils.nfl_api_utils import cached_request
from loguru import logger

# Load env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
NFL_API_KEY = os.getenv('NFL_API_KEY')
NFL_API_HOST = os.getenv('NFL_API_HOST')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # load data manager
        self.data_manager = DataManager()

        # load NFL API manager
        self.nfl_api_manager = NFLAPIManager(cache_dir="./cache")

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            logger.info(f'Connected to: {guild.name} (id: {guild.id})')
        
        # Load cogs after bot is ready
        await self.load_cogs()

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"❌ Command not found! Try `!help` for available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument! Check `!help {ctx.command}` for usage.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ You don't have permission to use this command!")
        else:
            logger.info(f"Error: {error}")
            await ctx.send(f"❌ An error occurred: {error}")

    async def load_cogs(self):
        """Load all command modules"""
        try:
            # Load Character commands
            await self.load_extension('commands.character_commands')
            logger.info("✅ Loaded Character commands")
            
            # Load NFL commands
            await self.load_extension('commands.nfl_commands')
            logger.info("✅ Loaded NFL commands")

            # Load Story commands
            await self.load_extension('commands.story_commands')
            logger.info("✅ Loaded Story commands")
            
        except Exception as e:
            logger.error(f"❌ Failed to load cogs: {e}")

# Create bot instance
bot = MyBot(command_prefix='!', intents=intents)

async def main():
    """Main function to start the bot"""
    try:
        await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())