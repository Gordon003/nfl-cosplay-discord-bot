from discord.ext import commands
from utils import read_csv

class NFLCommands(commands.Cog, name="NFL"):
    """NFL-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.teams_data = read_csv.get_teams_info()
        self.characters_data = read_csv.get_teams_character()
    
    @commands.command(name='team')
    async def team_info(self, ctx, *, team_name):
        await ctx.send(f"Team '{team_name}' not found!")


async def setup(bot):
    await bot.add_cog(NFLCommands(bot))