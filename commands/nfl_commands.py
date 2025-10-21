import os
import discord
from discord.ext import commands
from loguru import logger
from table2ascii import table2ascii, PresetStyle
from utils.color import COLOR_PURPLE
from utils.nfl_schedule import (
    get_next_scheduled_games_by_team_id,
    get_gameweek_by_offset,
)
from utils.date import convert_date, convert_short_date

nfl_matches_params = {"league": "NFL", "season": os.getenv("CURRENT_YEAR")}
nfl_api_matches_error = "Failed to get matches"


class NFLCommands(commands.Cog, name="NFL Commands"):

    def __init__(self, bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        self.nfl_api_manager = bot.nfl_api_manager

    @commands.group(name="nfl", invoke_without_command=True)
    async def nfl(self, ctx):
        # highlight commands
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🏈 NFL Commands",
                description="Use these commands to explore NFL teams and characters!",
                color=COLOR_PURPLE,
            )
            embed.add_field(
                name="Commands:",
                value="`!nfl gameweek <previous|current|next>` - Get gameweek schedule\n"
                "`!nfl schedule <team_name>` - Get team upcoming schedule\n",
                inline=False,
            )
            embed.add_field(
                name="Examples:",
                value="`!nfl gameweek previous`\n"
                "`!nfl gameweek current`\n"
                "`!nfl schedule cowboys`\n",
                inline=False,
            )
            await ctx.send(embed=embed)

    @nfl.command(
        name="gameweek",
        help="Get gameweek schedule",
    )
    async def get_gameweek(self, ctx, period: str = "current"):
        # get latest scores from NFL API
        try:
            response = await self.bot.nfl_api_manager.get_nfl_all_matches()
        except:
            await ctx.send(nfl_api_matches_error)
            return

        # get gameweek selection
        period_mapping = {"current": 0, "previous": -1, "next": 1}
        offset = period_mapping.get(period.lower(), 0)

        games = get_gameweek_by_offset(response["data"], offset)

        # get particular field of each game
        output_value_table = []
        for game in games:

            # game status emoji
            game_status_emoji = ""
            if game["state"]["description"] == "Scheduled":
                game_status_emoji = "⏳"
            elif game["state"]["description"] == "Finished":
                game_status_emoji = "✅"
            elif game["state"]["description"] == "In Progress":
                game_status_emoji = "🏈"
            else:
                game_status_emoji = "❓"

            output_value_table.append(
                [
                    convert_short_date(game["date"]),
                    game["homeTeam"]["abbreviation"],
                    game["awayTeam"]["abbreviation"],
                    game["state"]["score"]["current"],
                    game_status_emoji,
                ]
            )

        # display to discord
        output = table2ascii(
            header=["Date", "Home", "Away", "Score", "Status"],
            body=output_value_table,
            style=PresetStyle.thin_box,
        )
        embed = discord.Embed(
            title=f"🏈 {period.capitalize()} gameweek:",
            description=f"```\n{output}\n```",
        )
        await ctx.send(embed=embed)

    @nfl.command(
        name="schedule", help="Get team upcoming schedule", usage="<team_name>"
    )
    async def get_team_schedule(self, ctx, *, team_name):
        # get team ids from name
        team_name_lower = team_name.lower().replace(" ", "_")
        team_data = self.data_manager.get_team_data_by_team_key(team_name_lower)
        team_id = team_data["id"]

        # call nfl api
        try:
            response = await self.bot.nfl_api_manager.get_nfl_all_matches()
        except Exception as e:
            await ctx.send(f"Failed to get matches: {e}")
            return

        games = get_next_scheduled_games_by_team_id(response["data"], team_id)

        output_value_table = []
        for game in games:
            output_value_table.append(
                [
                    convert_date(game["date"]),
                    game["homeTeam"]["name"],
                    game["awayTeam"]["name"],
                ]
            )

        # get total drama character
        char_key = self.data_manager.get_character_key_by_team_key(team_name_lower)
        char_name = self.data_manager.get_character_data_by_character_key(char_key)[
            "name"
        ]

        # display to discord
        output = table2ascii(
            header=["Date", "Home Team", "Away Team"],
            body=output_value_table,
            style=PresetStyle.thin_box,
        )
        embed = discord.Embed(
            title=f"🏈 Upcoming matches for {char_name}'s {team_name.upper()}",
            description=f"```\n{output}\n```",
        )
        await ctx.send(embed=embed)

    @nfl.command(
        name="upcoming",
        help="Get upcoming week schedule",
    )
    async def get_upcoming_week_games(self, ctx):
        """Get latest scores from previous week"""
        try:
            response = await self.bot.nfl_api_manager.get_nfl_all_matches()
        except:
            await ctx.send(nfl_api_matches_error)
            return

        games = get_gameweek_by_offset(response["data"], offset=1)

        output_value_table = []
        for game in games:
            output_value_table.append(
                [
                    convert_short_date(game["date"]),
                    game["homeTeam"]["name"],
                    game["awayTeam"]["name"],
                ]
            )

        # display to discord
        output = table2ascii(
            header=["Date", "Home Team", "Away Team"],
            body=output_value_table,
            style=PresetStyle.thin_box,
        )
        embed = discord.Embed(
            title=f"🏈 Upcoming matches for this week:",
            description=f"```\n{output}\n```",
        )
        await ctx.send(embed=embed)

    @nfl.command(
        name="standings",
        help="Get current standings",
    )
    async def get_nfl_standings(self, ctx, *args):

        # Valid conferences and divisions
        valid_conferences = ["nfc", "afc"]
        valid_divisions = ["north", "east", "south", "west"]

        selected_conference = [conference.upper() for conference in valid_conferences]
        selected_division = [division.capitalize() for division in valid_divisions]

        # Clean and normalize the command
        if args:
            for arg in args:
                arg_lower = arg.lower()
                if arg_lower in valid_conferences:
                    selected_conference = [arg_lower.upper()]
                elif arg_lower in valid_divisions:
                    selected_division = [arg_lower.capitalize()]

        # API Call to get standings
        total_standings = []
        try:
            if "NFC" in selected_conference:
                nfc_standings = await self.nfl_api_manager.get_nfl_standings("nfc")
                total_standings += nfc_standings["data"][0]["data"]
            if "AFC" in selected_conference:
                afc_standings = await self.nfl_api_manager.get_nfl_standings("afc")
                total_standings += afc_standings["data"][0]["data"]
        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            await ctx.send(nfl_api_matches_error)
            return

        # get team records via dictionary (team_id as key)
        team_records = {}
        for team_standings in total_standings:
            team_id = team_standings["team"]["id"]
            team_record = ""
            for statistic in team_standings["statistics"]:
                if statistic["displayName"] == "Division Record":
                    team_record = statistic["value"]
            team_records[team_id] = team_record

        # separately display teams by conference and division
        for conference in selected_conference:
            for division in selected_division:

                # filtered teams based on conference and division
                filtered_teams = (
                    self.data_manager.get_teams_key_by_conference_and_division(
                        conference, division
                    )
                )

                # get team data with records
                filter_teams_data = [
                    [team["abbreviation"], team_records[team["id"]]]
                    for team in filtered_teams
                ]
                filter_teams_data.sort(key=lambda x: (x[1], x[0]))

                # display in discord-friendly table
                header = f"**{conference.upper()} {division.capitalize()} Division**\n"
                table_output = table2ascii(
                    header=["Team", "Record"],
                    body=filter_teams_data,
                    style=PresetStyle.thin_box,
                )

                embed = discord.Embed(
                    title=header,
                    description=f"```\n{table_output}\n```",
                )
                await ctx.send(embed=embed)

    @nfl.command(name="injuries", help="Get injuries for a team", usage="<team_name>")
    async def get_nfl_team_injuries(self, ctx, *, team_name):
        try:
            team_info = self.data_manager.get_team_data_by_team_key(team_name.lower())
            injuries = await self.nfl_api_manager.get_nfl_team_injuries(
                team_info["nflApiId"]
            )
        except Exception as e:
            logger.error(f"Failed to get injuries for {team_name}: {e}")
            await ctx.send(
                f"❌ Failed to get injuries for {team_name}. Please try again later."
            )
            return

        output_value_table = []
        for injury in injuries["injuries"]:
            output_value_table.append([injury["shortComment"]])

        # display to discord
        output = table2ascii(
            header=["Players Injuries"],
            body=output_value_table,
            style=PresetStyle.thin_box,
        )
        embed = discord.Embed(
            title=f"🏈 Injuries for {team_info['name']}",
            description=f"```\n{output}\n```",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NFLCommands(bot))
