import discord
from discord import app_commands, Interaction
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
# /ping ~~ Lets you know the time between sending a command and recieving a result
    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: Interaction):

        latency_ms = round(self.bot.latency * 1000) if self.bot.latency is not None else 0

        await interaction.response.send_message(f"Pong! {latency_ms}ms 🏓")

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))