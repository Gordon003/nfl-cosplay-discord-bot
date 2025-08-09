import random
import discord
from discord.ext import commands
from loguru import logger
from table2ascii import table2ascii, PresetStyle
from utils import parse_discord_arg

class CharacterCommands(commands.Cog, name="Character Commands"):

    def __init__(self, bot):
        self.bot = bot
        self.data_manager = bot.data_manager
    
    @commands.group(name='char', invoke_without_command=True)
    async def character_command(self, ctx):

        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📺🏈 Character NFL Commands",
                description="Use these commands to explore character-team assignments!",
                color=0x800080
            )
            embed.add_field(
                name="Commands:",
                value=
                    "`!char team <team_name>` - Get character for that team\n"
                    "`!char character <character_name>` - Get team for that character\n"
                    "`!char list` - Get all NFL teams with their assigned character\n"
                    "`!char random` - Get a random pairing of character and team\n"
                      ,
                inline=False
            )
            embed.add_field(
                name="Examples:",
                value=
                    "`!char character cowboys`\n"
                    "`!char team heather`\n"
                    "`!char list --sort-by character`\n"
                    "`!char random`\n",
                inline=False
            )
            await ctx.send(embed=embed)

    @character_command.command(
        name='character',
        help='Get the character assigned to that defined team',
        usage='<team_name>'
    )
    async def get_team_character(self, ctx, *, team_name):

        # get team info
        team_key = team_name.lower()
        team_info = self.data_manager.get_team_info_by_team_key(team_key)

        # get character info
        char_key = self.data_manager.get_character_key_by_team_key(team_key)
        char_info = self.data_manager.get_character_info_by_character_key(char_key)

        if char_key is None :
            await ctx.send(f"Team '{team_name}' not found!")
            return

        # display to Discord
        embed = discord.Embed(
            title=f"🏈 {team_info['name']}",
            description=f"**Character:** {char_info['name']}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @character_command.command(
        name='team',
        help='Get the team assigned to that defined character',
        usage='<character_name>'
    )
    async def get_character_name(self, ctx, *, character_name):

        logger.debug(f"Getting team for character: {character_name}")

        # get character info
        char_key = character_name.lower()
        char_info = self.data_manager.get_character_info_by_character_key(char_key)

        # get team info
        team_key = self.data_manager.get_team_key_by_character_key(char_key)
        team_info = self.data_manager.get_team_info_by_team_key(team_key)

        if team_key is None :
            await ctx.send(f"Character '{character_name}' not been assigned to a team!")
            return

        # display to Discord
        embed = discord.Embed(
            title=f"👩 {char_info['name']}",
            description=f"**Team:** {team_info['name']}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @character_command.command(
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
        for team_key in self.data_manager.get_all_team_keys():
            char_key = self.data_manager.get_character_key_by_team_key(team_key)
            char_name = self.data_manager.get_character_info_by_character_key(char_key)["name"]
            team_name = self.data_manager.get_team_info_by_team_key(team_key)["abbreviation"]
            character_team_map_list.append([char_name, team_name])

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

    @character_command.command(
        name='random',
        help='Get a random pairing of character and team',
    )
    async def show_random_team_character(self, ctx):
        """Get all teams and characters assigned to them"""

        # Get random character and team key
        rand_team_key = random.choice(list(self.data_manager.get_all_team_keys()))
        rand_char_key = self.data_manager.get_character_key_by_team_key(rand_team_key)

        # Get character and team info
        char_name = self.data_manager.get_character_info_by_character_key(rand_char_key)["name"]
        team_name = self.data_manager.get_team_info_by_team_key(rand_team_key)["name"]

        embed = discord.Embed(
            title=f"🏈 {team_name}",
            description=f"**Character:** {char_name}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))