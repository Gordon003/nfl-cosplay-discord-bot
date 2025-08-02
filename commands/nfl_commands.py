import discord
from discord.ext import commands
from table2ascii import table2ascii, PresetStyle
from utils.nfl_utils import filter_next_games_by_team_id
from utils.date import convert_date

class NFLCommands(commands.Cog, name="NFL Commands"):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='nfl', invoke_without_command=True)
    async def nfl(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🏈 NFL Commands",
                description="Use these commands to explore NFL teams and characters!",
                color=0x800080
            )
            embed.add_field(
                name="Commands:",
                value="`!nfl team <team_name>` - Get character for a team\n"
                      "`!nfl character <character_name>` - Get team for a character\n",
                inline=False
            )
            embed.add_field(
                name="Examples:",
                value="`!nfl team cowboys`\n"
                      "`!nfl character heather`\n",
                inline=False
            )
            await ctx.send(embed=embed)
    
    @nfl.command(
        name='schedule',
        help='Get team upcoming schedule',
        usage='<team_name>'
    )
    async def get_team_schedule(self, ctx, *, team_name):
        team_name_lower = team_name.lower().replace(' ', '_')
        team_data = self.bot.nfl_teams_data[team_name_lower]
        team_id = team_data["id"]
        try:
            params = {
                'league': 'NFL',
                'season': 2025
            }
            response = self.bot.cached_nfl_request("/matches", params)

            games = filter_next_games_by_team_id(response["data"], team_id)

            output_value_table = []
            for game in games:
                output_value_table.append([convert_date(game["date"]), game["homeTeam"]["name"], game["awayTeam"]["name"]])

            # display in discord-friendly table
            output = table2ascii(
                header=["Date", "Home", "Away"],
                body=output_value_table,
                style=PresetStyle.thin_box
            )

            # get total drama charater
            total_drama_char_id = self.bot.get_character_key_by_team(team_name_lower)
            total_drama_char_name = self.bot.total_drama_characters_data[total_drama_char_id]["name"]

            embed = discord.Embed(
                title=f"🏈 Upcoming matches for {total_drama_char_name}'s {team_name.upper()}",
                description=f"```\n{output}\n```",
            )
            await ctx.send(embed=embed)
        except Exception as e:
            print("error", e)
            await ctx.send(f"❌ An error occurred: {e}")


async def setup(bot):
    await bot.add_cog(NFLCommands(bot))