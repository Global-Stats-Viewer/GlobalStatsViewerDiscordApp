import discord
from config import (
    PREFIX,
)
from typing import List
from discord import app_commands, Interaction
from discord.ext import commands
import utils 

class StaffList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

# /staff-list ~~ Provides the usernames of the staff members on the Global Stats Viewer team
    @app_commands.command(name="staff-list", description="List staff team members")
    async def staff_list(self, interaction: Interaction):
        await interaction.response.defer()

        url = f"https://{PREFIX}.globalstatsviewer.com/api/getstafflist"

        data = await utils.fetch_json(url)
        if data is None:
            await interaction.followup.send(
                "Error fetching staff list. Please try again later."
            )
            return
        owners: List[str] = []
        admins: List[str] = []
        developers: List[str] = []
        moderators: List[str] = []
        helpers: List[str] = []

        for u in data:
            try:
                stype = int(u.get("staff_type", 0))
            except Exception:
                stype = 0
            if utils.has_role(stype, utils.staff_flags["OWNER"]):
                owners.append(utils.format_staff_user(u))
            if utils.has_role(stype, utils.staff_flags["ADMIN"]):
                admins.append(utils.format_staff_user(u))
            if utils.has_role(stype, utils.staff_flags["DEVELOPER"]):
                developers.append(utils.format_staff_user(u))
            if utils.has_role(stype, utils.staff_flags["MODERATOR"]):
                moderators.append(utils.format_staff_user(u))
            if utils.has_role(stype, utils.staff_flags["HELPER"]):
                helpers.append(utils.format_staff_user(u))

        embed = discord.Embed(title="Global Stats Viewer Staff", color=discord.Color.blue())
        if owners:
            embed.add_field(
                name="Owners",
                value="\n".join([f"{utils.emotes.get('owner', '')} {u}" for u in owners]),
                inline=False,
            )
        if admins:
            embed.add_field(
                name="Admins",
                value="\n".join([f"{utils.emotes.get('mod', '')} {u}" for u in admins]),
                inline=False,
            )
        if developers:
            embed.add_field(
                name="Developers",
                value="\n".join([f"{utils.emotes.get('dev', '')} {u}" for u in developers]),
                inline=False,
            )
        if moderators:
            embed.add_field(
                name="Moderators",
                value="\n".join([f"{utils.emotes.get('mod', '')} {u}" for u in moderators]),
                inline=False,
            )
        if helpers:
            embed.add_field(
                name="Helpers",
                value="\n".join([f"{utils.emotes.get('helper', '')} {u}" for u in helpers]),
                inline=False,
            )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(StaffList(bot))