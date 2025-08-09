import os
import time
import discord
from discord.ext import commands
from loguru import logger
from table2ascii import table2ascii, PresetStyle
from utils.nfl_schedule import get_next_scheduled_games_by_team_id, get_gameweek_by_offset
from utils.date import convert_date
from utils.data_util import get_big_win_template, get_character_key_by_team_key, get_small_win_template, get_team_by_conference_and_division, get_tie_template, get_upcoming_template

nfl_matches_params = {
    'league': 'NFL',
    'season': os.getenv('CURRENT_YEAR')
}
nfl_api_matches_error = 'Failed to get matches'

class StoryCommands(commands.Cog, name="Story Commands"):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='story', invoke_without_command=True)
    async def story(self, ctx):
        # highlight commands
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🏈 Story Commands",
                description="Use these commands to generate a story!",
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

    @story.command(
        name='gameweek',
        help='Generate a story for the gameweek',
    )
    async def story_gameweek(self, ctx, period: str='current'):
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

        await ctx.send(f"Here's the storyline for {period.capitalize()} gameweek...\n")

        # generate game story
        for game in games:

            home_team_key = game["homeTeam"]["name"].lower().replace(' ', '_')
            home_team_info = self.bot.nfl_teams_data[home_team_key]
            home_team_character_key = get_character_key_by_team_key(self.bot.nfl_team_character_mapping_data, home_team_key)
            home_team_character_info = self.bot.characters_data[home_team_character_key]

            away_team_key = game["awayTeam"]["name"].lower().replace(' ', '_')
            away_team_info = self.bot.nfl_teams_data[away_team_key]
            away_team_character_key = get_character_key_by_team_key(self.bot.nfl_team_character_mapping_data, away_team_key)
            away_team_character_info = self.bot.characters_data[away_team_character_key]

            await ctx.send(f"⚔️ **{home_team_character_info['name']}'s {game['homeTeam']['name']} vs {away_team_character_info['name']}'s {game['awayTeam']['name']}**")
            time.sleep(1)  # Simulate some delay for dramatic effect

            if game["state"]["description"] == "Finished":
                final_score = game["state"]["score"]["current"]
                home_score, away_score = final_score.split('-')
                score_margin = abs(int(home_score) - int(away_score))
                story = ""
                placeholder_text = ""
                winner = []
                loser = []

                if score_margin > 0:
                    if score_margin >= 20:
                        placeholder_text = get_big_win_template(self.bot.storyline_data)
                    else:
                        placeholder_text = get_small_win_template(self.bot.storyline_data)
                    if int(home_score) > int(away_score):
                        winner = [home_team_character_info['name'], home_team_info["name"], home_score]
                        loser = [away_team_character_info['name'], away_team_info["name"], away_score]
                    else:
                        winner = [away_team_character_info['name'], away_team_info["name"], away_score]
                        loser = [home_team_character_info['name'], home_team_info["name"], home_score]
                else:
                    placeholder_text = get_tie_template(self.bot.storyline_data)
                    winner = [home_team_character_info['name'], home_team_info["name"], home_score]
                    loser = [away_team_character_info['name'], away_team_info["name"], away_score]

                story = placeholder_text.format(
                    winner_character=winner[0],
                    winner_team=winner[1],
                    winner_score=winner[2],
                    loser_character=loser[0],
                    loser_team=loser[1],
                    loser_score=loser[2]
                )
                await ctx.send(f"{story}")
            elif game["state"]["description"] == "Scheduled":
                placeholder_text = get_upcoming_template(self.bot.storyline_data)
                story = placeholder_text.format(
                    team1_character=home_team_character_info['name'],
                    team1=home_team_info["name"],
                    team2_character=away_team_character_info['name'],
                    team2=away_team_info["name"],
                    game_time=convert_date(game["date"])
                )
                await ctx.send(f"{story}")


            time.sleep(2)  # Simulate some delay for dramatic effect

async def setup(bot):
    await bot.add_cog(StoryCommands(bot))