import os
import discord
from discord.ext import commands
from loguru import logger
from table2ascii import table2ascii, PresetStyle
from utils.nfl_schedule import get_next_scheduled_games_by_team_id, get_gameweek_by_offset
from utils.date import convert_date
from utils.data_util import get_character_key_by_team_key, get_team_key_by_conference_and_division

nfl_matches_params = {
    'league': 'NFL',
    'season': os.getenv('CURRENT_YEAR')
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
        char_key = get_character_key_by_team_key(self.bot.characters_nfl_mapping_data ,team_name_lower)
        char_name = self.bot.characters_data[char_key]["name"]

        # display to discord
        output = table2ascii(
            header=["Date", "Home Team", "Away Team"],
            body=output_value_table,
            style=PresetStyle.thin_box
        )
        embed = discord.Embed(
            title=f"🏈 Upcoming matches for {char_name}'s {team_name.upper()}",
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

    @nfl.command(
        name='standings',
        help='Get current standings',
    )
    async def get_nfl_standings(self, ctx, args: str = None):

        # Valid conferences and divisions
        valid_conferences = ['nfc', 'afc']
        valid_divisions = ['north', 'east', 'south', 'west']

        selected_conference = valid_conferences
        selected_division = valid_divisions

        # Clean and normalize the command
        if args is not None:
            args = args.strip().lower()
            args = args.split()
            for arg in args:
                if arg in valid_conferences:
                    selected_conference = [arg.upper()]
                elif arg in valid_divisions:
                    selected_division = [arg.capitalize()]

        # API Call to get standings
        try:
            afc_standings = self.bot.cached_nfl_request("/standings", {'year': 2025, 'leagueType': 'NFL', 'leagueName': 'American Football Conference'})
            nfc_standings = self.bot.cached_nfl_request("/standings", {'year': 2025, 'leagueType': 'NFL', 'leagueName': 'National Football Conference'})
            total_standings = [*afc_standings["data"], *nfc_standings["data"]]
        except:
            await ctx.send(nfl_api_matches_error)
            return
        
        output_str = ''
        for conference in selected_conference:
            logger.debug(f"Selected conference: {conference}")
            for division in selected_division:
                logger.debug(f"Selected division: {division}")
                temp_team = get_team_key_by_conference_and_division(self.bot.nfl_teams_data, conference, division)
                output_str += f"**{conference.upper()} {division.capitalize()} Division**\n"
                output_str += table2ascii(
                    header=["Team"],
                    body=[[team] for team in temp_team],
                    style=PresetStyle.thin_box
                )
                output_str += "\n"

        embed = discord.Embed(
            title=f"🏈 NFL Standings",
            description=f"```{output_str}```",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NFLCommands(bot))