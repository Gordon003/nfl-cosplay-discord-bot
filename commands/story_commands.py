import time
import discord
from discord.ext import commands
from utils.nfl_schedule import  get_gameweek_by_offset
from utils.date import convert_date

class StoryCommands(commands.Cog, name="Story Commands"):
    
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        self.nfl_api_manager = bot.nfl_api_manager

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
                    "`!story gameweek <previous|current|next>` - Generate Story week\n",
                inline=False
            )
            embed.add_field(
                name="Examples:",
                value=
                    "`!story gameweek previous`\n"
                    "`!story gameweek current`\n"
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
            response = await self.bot.nfl_api_manager.get_nfl_matches()
        except Exception as e:
            await ctx.send(f"Failed to get matches: {e}")
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

            game_id = game["id"]

            home_team_key = game["homeTeam"]["name"].lower().replace(' ', '_')
            home_team_info = self.data_manager.get_team_info_by_team_key(home_team_key)
            home_team_char_key = self.data_manager.get_character_key_by_team_key(home_team_key)
            home_team_char_info = self.data_manager.get_character_info_by_character_key(home_team_char_key)

            away_team_key = game["awayTeam"]["name"].lower().replace(' ', '_')
            away_team_info = self.data_manager.get_team_info_by_team_key(away_team_key)
            away_team_char_key = self.data_manager.get_character_key_by_team_key(away_team_key)
            away_team_char_info = self.data_manager.get_character_info_by_character_key(away_team_char_key)

            await ctx.send(f"⚔️ **{home_team_char_info['name']}'s {game['homeTeam']['name']} vs {away_team_char_info['name']}'s {game['awayTeam']['name']}** [Match ID: {game_id}]")
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
                        placeholder_text = self.data_manager.get_storyline_random_big_win()
                    else:
                        placeholder_text = self.data_manager.get_storyline_random_small_win()
                    if int(home_score) > int(away_score):
                        winner = [home_team_char_info['name'], home_team_info["name"], home_score]
                        loser = [away_team_char_info['name'], away_team_info["name"], away_score]
                    else:
                        winner = [away_team_char_info['name'], away_team_info["name"], away_score]
                        loser = [home_team_char_info['name'], home_team_info["name"], home_score]
                else:
                    placeholder_text = self.data_manager.get_storyline_random_tie()
                    winner = [home_team_char_info['name'], home_team_info["name"], home_score]
                    loser = [away_team_char_info['name'], away_team_info["name"], away_score]

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
                placeholder_text = self.data_manager.get_storyline_random_upcoming()
                story = placeholder_text.format(
                    team1_character=home_team_char_info['name'],
                    team1=home_team_info["name"],
                    team2_character=away_team_char_info['name'],
                    team2=away_team_info["name"],
                    game_time=convert_date(game["date"])
                )
                await ctx.send(f"{story}")

            separator = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            await ctx.send(separator)

            time.sleep(2)  # Simulate some delay for dramatic effect
    
    @story.command(
        name='game',
        help='Generate a story for a specific match by match ID',
    )
    async def story_game(self, ctx, match_id: str):

        # validate match ID
        if not match_id.isdigit():
            await ctx.send("Invalid match ID. Please provide a numeric match ID.")
            return
        
        # get latest scores from NFL API
        try:
            response = await self.bot.nfl_api_manager.get_nfl_specific_match(match_id)
        except Exception as e:
            await ctx.send(f"Failed to get match {match_id}: {e}")
            return
        
        game_response = response[0]
        
        home_team_key = game_response["homeTeam"]["name"].lower().replace(' ', '_')
        home_team_info = self.data_manager.get_team_info_by_team_key(home_team_key)
        home_team_char_key = self.data_manager.get_character_key_by_team_key(home_team_key)
        home_team_char_info = self.data_manager.get_character_info_by_character_key(home_team_char_key)

        away_team_key = game_response["awayTeam"]["name"].lower().replace(' ', '_')
        away_team_info = self.data_manager.get_team_info_by_team_key(away_team_key)
        away_team_char_key = self.data_manager.get_character_key_by_team_key(away_team_key)
        away_team_char_info = self.data_manager.get_character_info_by_character_key(away_team_char_key)

        await ctx.send(f"⚔️ **{home_team_char_info['name']}'s {game_response['homeTeam']['name']} vs {away_team_char_info['name']}'s {game_response['awayTeam']['name']}** [Match ID: {match_id}]")

        home_team_id = game_response["homeTeam"]["id"]
        home_score = 0
        away_team_id = game_response["awayTeam"]["id"]
        away_score = 0

        game_state = game_response["state"]
        game_period_key = ["firstPeriod", "secondPeriod", "thirdPeriod", "fourthPeriod"]
        for period in game_period_key:
            period_score = game_state['score'][period]
            home_period_score, away_period_score = [int(x.strip()) for x in period_score.split('-')]
            home_score += home_period_score
            away_score += away_period_score
            await ctx.send(f"**{period}** {home_score} - {away_score}")


async def setup(bot):
    await bot.add_cog(StoryCommands(bot))