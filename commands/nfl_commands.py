from discord import Color, Embed
from discord.ext import commands
from utils import read_csv
from table2ascii import table2ascii, PresetStyle

class NFLCommands(commands.Cog, name="NFL"):
    """NFL-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.teams_data = read_csv.get_teams_info()
        self.characters_data = read_csv.get_teams_character()
    
    @commands.command(
        name='team',
        help='Get the character assigned to a particular team',
        brief='Get character assigned to that team',
        description='This command finds which character is assigned to that particular team',
        usage='<team_name>'
    )
    async def get_team_character(self, ctx, *, team_name):
        assigned_character = None
        for char in self.characters_data[1:]:
            if char[0] == team_name:
                assigned_character = char[1]
                break
        if assigned_character:
            await ctx.send(f"Team '{team_name}' has been assigned character: {assigned_character}")
        else:
            await ctx.send(f"Team '{team_name}' not found!")

    @commands.command(
        name='teams',
        help='Output all NFL teams',
        brief='Output all NFL teams',
        description='This command outputs all NFL teams'
    )
    async def get_all_teams(self, ctx):
        team_name_list = []
        for team in self.teams_data[1:]:
            team_name_list.append(team[0])
        await ctx.send(f"All teams name: {sorted(team_name_list)}")

    @commands.command(
        name='character-nfl-teams',
        help='Output a table of [team, character]',
        brief='Output a table of [team, character]',
        description='This command outputs pairs of [team, character]'
    )
    async def get_all_teams_character(self, ctx):
        
        characters_list = []
        for character in self.characters_data[1:]:
            characters_list.append([character[0], character[1]])

        output = table2ascii(
            header=["Team", "Character"],
            body=characters_list,
            style=PresetStyle.thin_box
        )

        await ctx.send(f"```\n{output}\n```")


async def setup(bot):
    await bot.add_cog(NFLCommands(bot))