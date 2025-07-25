# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils.read_json import load_nfl_teams, load_characters_nfl_mapping, load_total_drama_characters
import asyncio

# Load env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # load data
        self.nfl_teams_data = load_nfl_teams()
        self.characters_nfl_mapping_data = load_characters_nfl_mapping()
        self.total_drama_characters_data = load_total_drama_characters()
        print("✅ Loaded Total Drama & NFL data")

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(f'Connected to: {guild.name} (id: {guild.id})')
        
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
            print(f"Error: {error}")
            await ctx.send(f"❌ An error occurred: {error}")

    async def load_cogs(self):
        """Load all command modules"""
        try:
            # Load Total Drama commands
            await self.load_extension('commands.total_drama_commands')
            print("✅ Loaded Total Drama commands")
            
            # Load NFL commands (when ready)
            # await self.load_extension('commands.nfl_commands')
            # print("✅ Loaded NFL commands")
            
        except Exception as e:
            print(f"❌ Failed to load cogs: {e}")

    def get_character_key_by_team(self, team_name):
        """Get character key assigned to a team"""
        team_key = team_name.lower().replace(' ', '_')
        for name in self.characters_nfl_mapping_data.keys():
            if self.characters_nfl_mapping_data[name]["assigned_team"] == team_key:
                return name
        return None

# Create bot instance
bot = MyBot(command_prefix='!', intents=intents)

async def main():
    """Main function to start the bot"""
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())