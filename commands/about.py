import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
import utils
from config import BOT_VERSION

class About(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="about", description="About Global Stats Viewer")
    async def about(self, interaction: Interaction):
        await interaction.response.defer()

        description = (
            "Global Stats Viewer aims to expand upon the idea of a stats viewer by creating a ranking system that takes all of your accomplishments in rated Geometry Dash levels. "
            "Extreme Demon difficulty rankings are provided by the AREDL. This project is NOT a Demon List; to submit records, you must link your GD account, AREDL profile, Pointercrate, or Pemonlist account. "
            "All completions from those sources will be tracked on the website."
        )

        embed = discord.Embed(
            title="Global Stats Viewer",
            url="https://globalstatsviewer.com/",
            description=description,
            color=discord.Color.red(),
        )

        embed.add_field(name="Bot version", value=f"`{BOT_VERSION}`", inline=False)
        embed.add_field(name="discord.py", value=f"`{discord.__version__}`", inline=False)

        embed.add_field(
            name="Sources",
            value=(
                f"{utils.emotes.get('gsv','')} [Global Stats Viewer](https://globalstatsviewer.com/)\n"
                f"{utils.emotes.get('ul','')} [Updated Leaderboard](<https://discord.com/invite/Uz7pd4d>)\n"
                f"{utils.emotes.get('gd-browser','')} [GDBrowser](https://gdbrowser.com/)\n"
                f"{utils.emotes.get('aredl','')} [AREDL](https://aredl.net/#/)\n"
                f"{utils.emotes.get('pointercrate','')} [Pointercrate](https://pointercrate.com/)\n"
                f"{utils.emotes.get('pemonlist','')} [Pemonlist](https://pemonlist.com/)\n"
                f"{utils.emotes.get('gddp','')} [GDDP](https://gddp.pro/)\n"
            ),
            inline=False,
        )

        embed.add_field(
            name="Community",
            value=f"Have a problem or want to discuss the Global Stats Viewer?\nJoin our Discord:\n{utils.emotes.get('gsv','')} [GSV Discord](https://discord.gg/rhrjDNEEuE)",
            inline=False,
        )

        embed.add_field(
            name="Source Code",
            value=f"The source code can be viewed on our\n {utils.emotes.get('github','')} [GitHub repository](https://github.com/Global-Stats-Viewer/GlobalStatsViewerDiscordApp)\nContribute if you would like to!",
            inline=False,
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(About(bot))