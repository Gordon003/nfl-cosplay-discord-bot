import random
import discord
from discord.ext import commands
from table2ascii import table2ascii, PresetStyle
from utils import parse_discord_arg

class TotalDramaCommands(commands.Cog, name="Total Drama Commands"):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='td', invoke_without_command=True)
    async def total_drama(self, ctx):
        """Total Drama NFL commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📺🏈 Total Drama NFL Commands",
                description="Use these commands to explore character-team assignments!",
                color=0x800080
            )
            embed.add_field(
                name="Commands:",
                value="`!td team <team_name>` - Get character for a team\n"
                      "`!td character <character_name>` - Get team for a character\n",
                inline=False
            )
            embed.add_field(
                name="Examples:",
                value="`!td team cowboys`\n"
                      "`!td character heather`\n",
                inline=False
            )
            await ctx.send(embed=embed)

    @total_drama.command(
        name='team',
        help='Get the character assigned to a particular team',
        usage='<team_name>'
    )
    async def get_team_character(self, ctx, *, team_name):
        """Get character assigned to a team"""

        # get team info
        team_key = team_name.lower()
        team_info = self.bot.nfl_teams_data[team_key]

        # get character info
        character_key = self.bot.get_character_key_by_team(team_key)
        character_info = self.bot.total_drama_characters_data[character_key]

        if character_key is None :
            await ctx.send(f"Team '{team_name}' not found!")
            return
        
        if character_info is None:
            await ctx.send(f"Character '{character_key}' has not been assigned a team!")
            return

        embed = discord.Embed(
            title=f"🏈 {team_info['name']}",
            description=f"**Character:** {character_info['name']}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @total_drama.command(
        name='list',
        help='Show all character-team assignments with optional sorting and filtering',
        usage='[--sort-by team|character]',
    )
    async def show_team_character_assignments(self, ctx, *, args: str = ""):
        """Get all teams and characters assigned to them"""

        # Get sort_by param from 
        try:
            sort_by =parse_discord_arg.parse_discord_argument(args, "--sort-by")
            if sort_by is None:
                sort_by = "team"
        except Exception as e:
            sort_by = "team" # default

        # Validate sort_by parameter
        valid_sorts = {
            'team': 'team_name',
            't': 'team_name',
            'character': 'character_name',
            'c': 'character_name'
        }

        if sort_by not in valid_sorts:
            await ctx.send(f"❌ Invalid --sort-by parameter: {sort_by}")
            return
            
        sort_by = valid_sorts[sort_by]

        # get each character and team info
        character_team_map_list = []
        for character_key in self.bot.characters_nfl_mapping_data.keys():
            character_name = self.bot.total_drama_characters_data[character_key]["name"]
            team_key = self.bot.characters_nfl_mapping_data[character_key]["assigned_team"]
            team_name = self.bot.nfl_teams_data[team_key]["abbreviation"]
            character_team_map_list.append([character_name, team_name])

        if sort_by == 'team_name':
            character_team_map_list.sort(key=lambda x: x[1])
        elif sort_by == 'character_name':
            character_team_map_list.sort(key=lambda x: x[0])

        # display in discord-friendly table
        output = table2ascii(
            header=["Character", "Team"],
            body=character_team_map_list,
            style=PresetStyle.thin_box
        )
        await ctx.send(f"```\n{output}\n```")

    @total_drama.command(
        name='random',
        help='Get a random pairing of character and team',
    )
    async def show_random_team_character(self, ctx):
        """Get all teams and characters assigned to them"""

        # Get random character and team key
        rand_char_key = random.choice(list(self.bot.characters_nfl_mapping_data.keys()))
        rand_team_key = self.bot.characters_nfl_mapping_data[rand_char_key]["assigned_team"] 

        # Get character and team info
        character_name = self.bot.total_drama_characters_data[rand_char_key]["name"]
        team_name = self.bot.nfl_teams_data[rand_team_key]["name"]

        embed = discord.Embed(
            title=f"🏈 {team_name}",
            description=f"**Character:** {character_name}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(TotalDramaCommands(bot))