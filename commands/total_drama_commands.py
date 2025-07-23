import discord
from discord.ext import commands

class TotalDramaCommands(commands.Cog):

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
        team_key = team_name.lower()
        team_info = self.bot.nfl_teams_data[team_key]
        print("team_info", team_info)
        character_key = self.bot.get_character_key_by_team(team_key)
        print("character_key", character_key)
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

async def setup(bot):
    await bot.add_cog(TotalDramaCommands(bot))