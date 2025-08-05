import discord
from discord.ext import commands
from table2ascii import table2ascii, PresetStyle
from utils.nfl_schedule import get_next_scheduled_games_by_team_id, get_gameweek_by_offset
from utils.date import convert_date
from utils.data_util import get_character_key_by_team

nfl_matches_params = {
    'league': 'NFL',
    'season': 2025
}
nfl_api_matches_error = 'Failed to get matches'

class NFLCommands(commands.Cog, name="NFL Commands"):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='nfl', invoke_without_command=True)
    async def nfl(self, ctx):
        # highlight commands
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🏈 NFL Commands",
                description="Use these commands to explore NFL teams and characters!",
                color=0x800080
            )
            embed.add_field(
                name="Commands:",
                value=
                    "`!nfl gameweek <previous|current|next>` - Get gameweek schedule\n"
                    "`!nfl schedule <team_name>` - Get team upcoming schedule\n",
                inline=False
            )
            embed.add_field(
                name="Examples:",
                value=
                    "`!nfl gameweek previous`\n"
                    "`!nfl gameweek current`\n"
                    "`!nfl schedule cowboys`\n",
                inline=False
            )
            await ctx.send(embed=embed)

    @nfl.command(
        name='gameweek',
        help='Get gameweek schedule',
    )
    async def get_gameweek(self, ctx, period: str='current'):
        # get latest scores from NFL API
        try:
            response = self.bot.cached_nfl_request("/matches", nfl_matches_params)
        except:
            await ctx.send(nfl_api_matches_error)
            return

        # get gameweek selection
        period_mapping = {
            'current': 0,
            'previous': -1,
            'next': 1
        }
        offset = period_mapping.get(period.lower(), 0)

        games = get_gameweek_by_offset(response["data"], offset)
        
        # get particular field of each game
        output_value_table = []
        for game in games:
            output_value_table.append([convert_date(game["date"]), game["homeTeam"]["name"], game["awayTeam"]["name"], game["state"]["score"]["current"], game["state"]["description"]])

        # display to discord
        output = table2ascii(
            header=["Date", "Home", "Away", "Score", "Status"],
            body=output_value_table,
            style=PresetStyle.thin_box
        )
        embed = discord.Embed(
            title=f"🏈 {period.capitalize()} gameweek:",
            description=f"```\n{output}\n```",
        )
        await ctx.send(embed=embed)
    
    @nfl.command(
        name='schedule',
        help='Get team upcoming schedule',
        usage='<team_name>'
    )
    async def get_team_schedule(self, ctx, *, team_name):
        # get team ids from name
        team_name_lower = team_name.lower().replace(' ', '_')
        team_data = self.bot.nfl_teams_data[team_name_lower]
        team_id = team_data["id"]

        # call nfl api
        try:
            response = self.bot.cached_nfl_request("/matches", nfl_matches_params)
        except Exception as e:
            await ctx.send(nfl_api_matches_error)
            return

        games = get_next_scheduled_games_by_team_id(response["data"], team_id)

        output_value_table = []
        for game in games:
            output_value_table.append([convert_date(game["date"]), game["homeTeam"]["name"], game["awayTeam"]["name"]])

        # get total drama character
        total_drama_char_key = get_character_key_by_team(self.bot.characters_nfl_mapping_data ,team_name_lower)
        total_drama_char_name = self.bot.total_drama_characters_data[total_drama_char_key]["name"]

        # display to discord
        output = table2ascii(
            header=["Date", "Home Team", "Away Team"],
            body=output_value_table,
            style=PresetStyle.thin_box
        )
        embed = discord.Embed(
            title=f"🏈 Upcoming matches for {total_drama_char_name}'s {team_name.upper()}",
            description=f"```\n{output}\n```",
        )
        await ctx.send(embed=embed)

    @nfl.command(
        name='upcoming',
        help='Get upcoming week schedule',
    )
    async def get_upcoming_week_games(self, ctx):
        """ Get latest scores from previous week"""
        try:
            response = self.bot.cached_nfl_request("/matches", nfl_matches_params)
        except:
            await ctx.send(nfl_api_matches_error)
            return

        games = get_gameweek_by_offset(response["data"], offset=1)
        
        output_value_table = []
        for game in games:
            output_value_table.append([convert_date(game["date"]), game["homeTeam"]["name"], game["awayTeam"]["name"]])

        # display to discord
        output = table2ascii(
            header=["Date", "Home Team", "Away Team"],
            body=output_value_table,
            style=PresetStyle.thin_box
        )
        embed = discord.Embed(
                title=f"🏈 Upcoming matches for this week:",
                description=f"```\n{output}\n```",
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NFLCommands(bot))