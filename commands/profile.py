import discord
from config import (
    PREFIX,
)
from typing import List, Optional
from discord import app_commands, Interaction
from discord.ext import commands
import utils 

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
# /profile ~~ Lets the user view the GSV profile of any GSV, Discord, GD, AREDL, Pointercrate, or Pemonlist ID
    @app_commands.command(name="profile", description="Display a user profile")
    @app_commands.describe(
        id="Id of user",
        source="Lookup source",
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
        ]
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        id: Optional[str] = None,
        source: Optional[app_commands.Choice[str]] = None,
    ):
        await interaction.response.defer()
        auto_added = False
        username = False

        if id is None and source is None:
            auto_added = True
            source_value = "discord_id"
            id = str(interaction.user.id)
        elif id is not None and source is None:
            source_value = "gsv_registered"
        else:
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
            unregistered = not registered

        if data is None:
            await interaction.followup.send(
                "Error fetching profile. Please try again later."
            )
            return
        player_info = data.get("player_info", {})
        classic_rank = data.get("classic_rank", {})
        platformer_rank = data.get("platformer_rank", {})
        socials = data.get("socials", {})
        country_data = player_info.get("country_data", {})

        raw_id = player_info.get("id")

        embed = discord.Embed(
            color=discord.Color(
                int(
                    str(player_info.get("accent_color")).replace("#", "").replace("0x", ""),
                    16,
                )
            )
            if player_info.get("accent_color")
            else discord.Color.yellow(),
        )

        embed.set_author(
            name=player_info.get("username", "Unknown"),
            icon_url=player_info.get("profile_picture", ""),
        )

        id_label = "User" if registered else "Profile"
        page_text = "[User Page]" if registered else "[Profile Page]"

        page_url = (
            f"https://globalstatsviewer.com/users/{raw_id}"
            if registered
            else f"https://globalstatsviewer.com/profiles/{raw_id}"
        )

        registered_text = f"Registered {utils.emotes['check']}" if registered else ""

        header_value = f"{utils.emotes['gsv']} {page_text}({page_url})\n{registered_text}"

        embed.add_field(
            name=f"{id_label} ID: `{raw_id}`",
            value=header_value,
            inline=False,
        )

        if auto_added and unregistered:
            embed.add_field(
                name="Claim this profile:",
                value=(
                    f"This looks like your Discord profile. "
                    f"Claim it on globalstatsviewer.com"
                ),
                inline=False,
            )

        embed.add_field(name="\n", value="_ _")

        classic_points = classic_rank.get("points", 0)
        platformer_points = platformer_rank.get("points", 0)
        classic_global_rank = classic_rank.get("global_rank", "N/A")
        platformer_global_rank = platformer_rank.get("global_rank", "N/A")

        embed.add_field(
            name="Ranking:",
            value=f"Classic: `{classic_points}pts` *#{classic_global_rank}*\n"
            f"Platformer: `{platformer_points}pts` *#{platformer_global_rank}*\n",
            inline=False,
        )

        embed.add_field(name="\n", value="_ _")

        socials_list = []
        if socials.get("youtube"):
            socials_list.append(f"{utils.emotes['youtube']} [YouTube]({socials['youtube']})")
        if socials.get("twitter"):
            socials_list.append(f"{utils.emotes['twitter']} [Twitter]({socials['twitter']})")
        if socials.get("twitch"):
            socials_list.append(f"{utils.emotes['twitch']} [Twitch]({socials['twitch']})")
        if socials.get("geometry_dash"):
            socials_list.append(
                f"{utils.emotes['gd-browser']} [GDBrowser](https://gdbrowser.com/u/{socials['geometry_dash']})"
            )
        if socials.get("aredl"):
            socials_list.append(
                f"{utils.emotes['aredl']} [AREDL](https://aredl.net/profiles/{socials['aredl']})"
            )
        if socials.get("pointercrate"):
            socials_list.append(
                f"{utils.emotes['pointercrate']} [Pointercrate](https://pointercrate.com/demonlist/statsviewer/?player={socials['pointercrate']})"
            )
        if socials.get("pemonlist"):
            socials_list.append(
                f"{utils.emotes['pemonlist']} [Pemonlist](https://globalstatsviewer.com/pemonlist/{socials['pemonlist']})"
            )

        if socials_list:
            embed.add_field(name="Socials:", value=("\n".join(socials_list)), inline=False)

        embed.add_field(name="\n", value="_ _")

        countries: List[str] = []
        country = country_data.get("country", {}) or {}
        subdivision = country_data.get("subdivision", {}) or {}
        secondary_country = country_data.get("secondary_country", {}) or {}

        if country.get("name"):
            countries.append(str(country["name"]))
        if subdivision.get("name"):
            countries.append(str(subdivision["name"]))
        if secondary_country.get("name"):
            countries.append(str(secondary_country["name"]))

        footer_text = " | ".join(countries) if countries else ""
        code = country.get("code")
        icon_url = f"https://flagcdn.com/w40/{str(code).lower()}.png" if code else None
        if icon_url:
            embed.set_footer(text=footer_text, icon_url=icon_url)
        else:
            embed.set_footer(text=footer_text)

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))