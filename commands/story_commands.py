import time
import discord
from discord.ext import commands
from loguru import logger
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

        # Final message after all games
        await ctx.send(f"And that's it for this gameweek. Stay tuned for the next one. 🏈")
    
    @story.command(
        name='match',
        help='Generate a story for a specific match by match ID',
    )
    async def story_match(self, ctx, match_id: str):

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
        home_team_id = game_response["homeTeam"]["id"]
        home_team_char_key = self.data_manager.get_character_key_by_team_key(home_team_key)
        home_team_char_info = self.data_manager.get_character_info_by_character_key(home_team_char_key)

        away_team_key = game_response["awayTeam"]["name"].lower().replace(' ', '_')
        away_team_info = self.data_manager.get_team_info_by_team_key(away_team_key)
        away_team_id = game_response["awayTeam"]["id"]
        away_team_char_key = self.data_manager.get_character_key_by_team_key(away_team_key)
        away_team_char_info = self.data_manager.get_character_info_by_character_key(away_team_char_key)

        await ctx.send(f"⚔️ **{home_team_char_info['name']}'s {game_response['homeTeam']['name']} vs {away_team_char_info['name']}'s {game_response['awayTeam']['name']}** [Match ID: {match_id}]")
        time.sleep(2)

        # stadium & forecast
        venue = game_response["venue"]
        forecast = game_response["forecast"]
        await ctx.send(f"🎤 Welcome to {venue['city']} as the forecast is {forecast['status']} at the temperature of {forecast['temperature']}")
        time.sleep(2)

        home_score = 0
        away_score = 0

        game_period_key = ["firstPeriod", "secondPeriod", "thirdPeriod", "fourthPeriod"]
        game_period_text = ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"]

        game_state = game_response["state"]
        game_events = game_response["events"]

        START = True
        period_index = 0
        for event in game_events:

            result = event["result"]
            end = event["end"]
            team = event["team"]

            # get current team
            offensive_team = None
            offensive_char = None
            defensive_team = None
            defensive_char = None
            if team["id"] == home_team_id:
                offensive_team = home_team_info
                offensive_char = home_team_char_info
                defensive_team = away_team_info
                defensive_char = away_team_char_info
            elif team["id"] == away_team_id:
                offensive_team = away_team_info
                offensive_char = away_team_char_info
                defensive_team = home_team_info
                defensive_char = home_team_char_info

            # start of the game
            if START == True:
                await ctx.send(f"**{game_period_text[period_index]}**: {offensive_char['name']}'s {offensive_team['nickname']} starts with the ball!")
                time.sleep(2)
                START = False

            # if play finished in the next period
            if end["period"] != game_period_text[period_index]:
                await ctx.send(f"💣 And that's the end of the {game_period_text[period_index]}")
                time.sleep(1)
                period_score = game_state['score'][game_period_key[period_index]]
                home_period_score, away_period_score = [int(x.strip()) for x in period_score.split('-')]
                home_score += home_period_score
                away_score += away_period_score
                await ctx.send(f"**At the end of {game_period_text[period_index]}:** it's {home_team_char_info['name']} {home_score} - {away_score} {away_team_char_info['name']}")
                time.sleep(1)
                period_index += 1

            placeholder_text = None
            if result == "Touchdown":
                placeholder_text = self.data_manager.get_game_event_random_touchdown()
            elif result == "Field Goal":
                placeholder_text = self.data_manager.get_game_event_random_field_goal()
            elif result == "Interception":
                placeholder_text = self.data_manager.get_game_event_random_interception()

            if placeholder_text is not None:
                story = placeholder_text.format(
                    offensive_character=offensive_char['name'],
                    offensive_team=offensive_team["nickname"],
                    defensiv_character=defensive_char['name'],
                    defensive_team=defensive_team["nickname"],
                )
                await ctx.send(f"{story}") 
                time.sleep(2)

            # Game finished at the end of the current period or next period
            if end["clock"] is None or end["period"] != game_period_text[period_index]:
                await ctx.send(f"💣 That's the end of the {game_period_text[period_index]}")
                time.sleep(1)
                period_score = game_state['score'][game_period_key[period_index]]
                home_period_score, away_period_score = [int(x.strip()) for x in period_score.split('-')]
                home_score += home_period_score
                away_score += away_period_score
                await ctx.send(f"**At the end of {game_period_text[period_index]}:** it's {home_team_char_info['name']} {home_score} - {away_score} {away_team_char_info['name']}")
                time.sleep(1)
                period_index += 1

        # Show the winner of the game
        winner = None
        loser = None
        winner_score = 0
        loser_score = 0
        if home_score > away_score:
            winner = home_team_char_info['name']
            loser = away_team_char_info['name']
            winner_score = home_score
            loser_score = away_score
        elif away_score > home_score:
            winner = away_team_char_info['name']
            loser = home_team_char_info['name']
            winner_score = away_score
            loser_score = home_score

        if winner is not None and loser is not None:
            await ctx.send(f"🏆 **{winner}** wins against **{loser}** with the score of {winner_score} - {loser_score}!")
        else:
            await ctx.send(f"🏆 It's a tie! Both teams scored {home_score} - {away_score}!")


        # game_state = game_response["state"]
        # game_period_key = ["firstPeriod", "secondPeriod", "thirdPeriod", "fourthPeriod"]
        # for period in game_period_key:
        #     period_score = game_state['score'][period]
        #     home_period_score, away_period_score = [int(x.strip()) for x in period_score.split('-')]
        #     home_score += home_period_score
        #     away_score += away_period_score
        #     await ctx.send(f"**{period}** {home_score} - {away_score}")


async def setup(bot):
    await bot.add_cog(StoryCommands(bot))