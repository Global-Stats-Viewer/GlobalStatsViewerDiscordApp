import discord
from config import (
    PREFIX,
)
from typing import List
from discord import app_commands, Interaction
from discord.ext import commands
from discord.ui import Button, View
import utils 

class Completions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
# /completions ~~ Lets the user view completions of any searched profile, can be toggled to be Classic or Platformer completions
    @app_commands.command(name="completions", description="Displays a user completions")
    @app_commands.describe(
        id="ID of user",
        source="Lookup source",
        gamemode="Show platformer/classic completions?",
    )
    @app_commands.choices(
        source=[
            app_commands.Choice(name="GSV Registered", value="gsv_registered"),
            app_commands.Choice(name="GSV Unregistered", value="gsv_unregistered"),
            app_commands.Choice(name="Discord ID", value="discord_id"),
            app_commands.Choice(name="GD Account ID", value="geometry_dash"),
            app_commands.Choice(name="AREDL", value="aredl"),
            app_commands.Choice(name="Pointercrate", value="pointercrate"),
            app_commands.Choice(name="Pemonlist", value="pemonlist"),
        ],
        gamemode=[
            app_commands.Choice(name="Classic", value="classic"),
            app_commands.Choice(name="Platformer", value="platformer"),
        ],
    )
    async def completions(
        self,
        interaction: discord.Interaction,
        id: str,
        source: app_commands.Choice[str],
        gamemode: app_commands.Choice[str],
    ):
        await interaction.response.defer()
        mode = getattr(gamemode, "value", str(gamemode)).lower()
        username = False

        source_value = getattr(source, "value", str(source))
        registered = source_value == "gsv_registered"
        unregistered = source_value == "gsv_unregistered"

        if source_value == "discord_id":
            id_str = id.strip()
            digits = "".join(ch for ch in id_str if ch.isdigit())
            if digits:
                id = digits
            else:
                member = None
                if interaction.guild:
                    member = interaction.guild.get_member_named(id_str)
                    if not member:
                        try:
                            members = await interaction.guild.query_members(query=id_str, limit=1)
                            member = members[0] if members else None
                        except Exception:
                            member = None
                if member:
                    id = str(member.id)
                else:
                    await interaction.followup.send(
                        "Bad format, please send a Discord ID or username that is on this server."
                    )
                    return
        elif source_value == "gsv_registered" or source_value == "gsv_unregistered":
            try:
                int(id)
            except ValueError:
                username = True
        elif source_value == "gsv_unregistered" or source_value == "gsv_unregistered":
            try:
                int(id)
            except ValueError:
                username = True
        elif source_value == "geometry_dash":
            try:
                int(id)
            except ValueError:
                await interaction.followup.send(
                    "Bad format, please send your geometry dash id not nickname."
                )
                return
        elif source_value == "pointercrate":
            try:
                int(id)
            except ValueError:
                await interaction.followup.send(
                    "Bad format, please send your pointercrate id not nickname."
                )
                return

        if registered and not username:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(id)}"
            )
            data = await utils.fetch_json(api_url)
        elif registered and username:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(id)}?type=username"
            )
            data = await utils.fetch_json(api_url)
        elif unregistered and username:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getprofilebasicinfo/{str(id)}?type=username"
            )
            data = await utils.fetch_json(api_url)
        elif unregistered:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getprofilebasicinfo/{str(id)}"
            )
            data = await utils.fetch_json(api_url)
        else:
            data, registered = utils.fetch_both_ways_info(str(id), source_value)

        if data is None:
            await interaction.followup.send(
                "Error fetching profile. Please try again later."
            )
            return

        player_info = data.get("player_info", {})
        username = player_info.get("username")
        pfp = player_info.get("profile_picture")
        raw_id = player_info.get("id")

        user_url = (
            f"https://globalstatsviewer.com/users/{raw_id}"
            if registered
            else f"https://globalstatsviewer.com/profiles/{raw_id}"
        )

        mode = getattr(gamemode, "value", str(gamemode)).lower()


        if registered and not username:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getusercompletions/{id}?type={mode}"
            )
            data = await utils.fetch_json(api_url)
        elif registered and username:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getusercompletions/{id}?type={mode}&completions_type={"username"}"
            )
            data = await utils.fetch_json(api_url)
        elif unregistered and username:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getprofilecompletions/{id}?type={mode}&completions_type={"username"}"
            )
            data = await utils.fetch_json(api_url)
        elif unregistered:
            api_url = (
                f"https://{PREFIX}.globalstatsviewer.com/api/getprofilecompletions/{id}?type={mode}"
            )
            data = await utils.fetch_json(api_url)
        else:
            data, registered = utils.fetch_both_ways_comp(str(id), mode, source_value)

        if data is None:
            await interaction.followup.send(
                "Error fetching profile. Please try again later."
            )
            return

        completions_data = data.get("demonlist", [])

        platformer = mode == "platformer"
        max_pages = (max(len(completions_data), 1) - 1) // 8
        page = 0

        def build_embed(page: int) -> discord.Embed:

            embed = discord.Embed(
                title=f"{username}",
                url=user_url,
                color=discord.Color(
                    int(
                        str(data.get("user_accent_color"))
                        .replace("#", "")
                        .replace("0x", ""),
                        16,
                    )
                )
                if data.get("user_accent_color")
                else discord.Color.green(),
            )

            embed.set_author(name=username, icon_url=pfp)

            begin = page * 8
            end = min(begin + 8, len(completions_data))
            completions = []
            for i in range(begin, end):
                level = completions_data[i]
                name = level.get("level_name")
                video = level.get("video")
                shown = f" [{name}]({video})" if video else f"{name}"
                pos = level.get("position")
                pos_text = f" (#{pos})" if pos is not None else ""
                if platformer:
                    level_emote = f"{utils.emotes['youtube']}"
                else:
                    gddp_tier = level.get("gddp_tier", {})
                    tier_name = gddp_tier.get("name")
                    emote = utils.gddp_emote_for_tier(tier_name) if tier_name else ""
                    level_emote = emote if emote else "."
                completions.append(f"{level_emote} {shown} {pos_text}")
            value = "\n".join(completions) if completions else "No records found."

            remaining = max(len(completions_data) - end, 0)
            if remaining > 0:
                value += f"\n*and {remaining} others*"

            section_name = "Platformer Records" if platformer else "Demon Records"
            embed.add_field(name=section_name, value=value, inline=False)

            embed.set_footer(text=f"Page: {page+1}/{max_pages+1}")

            return embed

        prev = Button(label="Prev", style=discord.ButtonStyle.red)
        next = Button(label="Next", style=discord.ButtonStyle.green)

        async def go_back(new_interaction: discord.Interaction):
            nonlocal page
            await new_interaction.response.defer()
            page = max(page - 1, 0)
            await new_interaction.edit_original_response(embed=build_embed(page), view=view)

        async def go_next(new_interaction: discord.Interaction):
            nonlocal page
            await new_interaction.response.defer()
            page = 0 if page + 1 > max_pages else page + 1
            await new_interaction.edit_original_response(embed=build_embed(page), view=view)

        prev.callback = go_back
        next.callback = go_next

        view = View()
        view.add_item(prev)
        view.add_item(next)

        await interaction.followup.send(embed=build_embed(page), view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Completions(bot))