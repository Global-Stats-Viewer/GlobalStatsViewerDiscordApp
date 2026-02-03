# bot.py
# -- Discord bot

from config import IS_DEV_ENV, DEV_STATUS, LOCAL_TOKEN, EMOTES, PROD_TOKEN, PREFIX, BOT_VERSION
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import os

import discord
import requests
from discord import app_commands
from discord.ui import Button, View

# >> Bot Constructor
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Code -----------------------------------------------------------------------------------------------

emotes = EMOTES["dev"] if IS_DEV_ENV == DEV_STATUS.LOCAL_BOT else EMOTES["prod"]

staff_flags = {
    "OWNER": 1,
    "ADMIN": 2,
    "DEVELOPER": 4,
    "MODERATOR": 8,
    "HELPER": 16,
}

def has_role(staff_type: int, role: int) -> bool:
    return (staff_type & role) == role

def gddp_emote_for_tier(tier_name: str) -> str:
    try:
        if not tier_name:
            return ""
        return emotes.get(tier_name.lower(), "")
    except Exception:
        return ""

def format_staff_user(user: Dict[str, Any]) -> str:
    username = user.get("username", "Unknown")
    user_id = user.get("id")
    if user_id is None:
        return str(username)
    return f"[{username}](https://globalstatsviewer.com/users/{user_id})"

def resolve_user_profile_ids(data: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    player_info = data.get("player_info", {}) or {}
    user_id = data.get("user_id") or player_info.get("user_id")
    profile_id = data.get("profile_id") or player_info.get("profile_id")
    raw_id = data.get("id") or player_info.get("id")
    if user_id is None and raw_id is not None:
        user_id = raw_id
    if profile_id is None and raw_id is not None:
        profile_id = raw_id
    user_id_str = str(user_id) if user_id is not None else None
    profile_id_str = str(profile_id) if profile_id is not None else None
    return user_id_str, profile_id_str


# /about ~~ Provides information about the Global Stats Viewer project, bot version, sources, and a link to the Discord server
@tree.command(name="about", description="About Global Stats Viewer")
async def about(interaction: discord.Interaction):
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
            f"{emotes['gsv']} [Global Stats Viewer](https://globalstatsviewer.com/)\n"
            f"{emotes['ul']} [Updated Leaderboard](<https://discord.com/invite/Uz7pd4d>)\n"
            f"{emotes['gd-browser']} [GDBrowser](https://gdbrowser.com/)\n"
            f"{emotes['aredl']} [AREDL](https://aredl.net/#/)\n"
            f"{emotes['pointercrate']} [Pointercrate](https://pointercrate.com/)\n"
            f"{emotes['pemonlist']} [Pemonlist](https://pemonlist.com/)\n"
            f"{emotes['gddp']} [GDDP](https://gddp.pro/)\n"
        ),
        inline=False,
    )

    embed.add_field(
        name="Community",
        value=f"Have a problem or want to discuss the Global Stats Viewer?\nJoin our Discord:\n{emotes['gsv']} [GSV Discord](https://discord.gg/rhrjDNEEuE)\nMake a issue on github:\n{emotes['github']} [Bot github](https://github.com/Global-Stats-Viewer/GlobalStatsViewerDiscordApp)",
        inline=False,
    )

    await interaction.followup.send(embed=embed)


# /ping ~~ Lets you know the time between sending a command and recieving a result
@tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):

    latency_ms = round(client.latency * 1000) if client.latency is not None else 0

    await interaction.response.send_message(f"Pong! {latency_ms}ms 🏓")


# /staff-list ~~ Provides the usernames of the staff members on the Global Stats Viewer team
@tree.command(name="staff-list", description="List staff team members")
async def staff_list(interaction: discord.Interaction):
    await interaction.response.defer()
    url = f"https://{PREFIX}.globalstatsviewer.com/api/getstafflist"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        await interaction.followup.send("Error fetching staff llist. Please try again later.")
        return

    owners = [format_staff_user(user) for user in data if has_role(int(user.get("staff_type", 0)), staff_flags["OWNER"])]
    developers = [format_staff_user(user) for user in data if has_role(int(user.get("staff_type", 0)), staff_flags["DEVELOPER"])]
    admins = [format_staff_user(user) for user in data if has_role(int(user.get("staff_type", 0)), staff_flags["ADMIN"])]
    moderators = [format_staff_user(user) for user in data if has_role(int(user.get("staff_type", 0)), staff_flags["MODERATOR"])]
    helpers = [format_staff_user(user) for user in data if has_role(int(user.get("staff_type", 0)), staff_flags["HELPER"])]

    embed = discord.Embed(title="Global Stats Viewer Staff", color=discord.Color.blue())
    
    if owners:
        embed.add_field(name="Owners", value="\n".join([f"{emotes.get('owner', '')} {u}" for u in owners]), inline=False)
    if admins:
        embed.add_field(name="Admins", value="\n".join([f"{emotes.get('mod', '')} {u}" for u in admins]), inline=False)
    if developers:
        embed.add_field(name="Developers", value="\n".join([f"{emotes.get('dev', '')} {u}" for u in developers]), inline=False)
    if moderators:
        embed.add_field(name="Moderators", value="\n".join([f"{emotes.get('mod', '')} {u}" for u in moderators]), inline=False)
    if helpers:
        embed.add_field(name="Helpers", value="\n".join([f"{emotes.get('helper', '')} {u}" for u in helpers]), inline=False)

    await interaction.followup.send(embed=embed)


# /profile ~~ Lets the user view the GSV profile of any GSV, Discord, GD, AREDL, Pointercrate, or Pemonlist ID
@tree.command(name="profile", description="Display a user profile")
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
    interaction: discord.Interaction,
    id: str,
    source: app_commands.Choice[str],
):
    await interaction.response.defer()

    source_value = getattr(source, "value", str(source))
    registered = source_value == "gsv_registered"
    unregistered = source_value == "gsv_unregistered"

    if registered:
        api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(id)}"
    elif unregistered:
        api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getprofilebasicinfo/{str(id)}"
    else:
        api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(id)}?type={source_value}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        await interaction.followup.send("Error fetching user data. Please try again.")
        return

    player_info = data.get("player_info", {})
    classic_rank = data.get("classic_rank", {})
    platformer_rank = data.get("platformer_rank", {})
    socials = data.get("socials", {})
    country_data = player_info.get("country_data", {})

    resolved_user_id, resolved_profile_id = resolve_user_profile_ids(data)

    embed = discord.Embed(
        color=discord.Color(
            int(str(player_info.get("accent_color")).replace("#", "").replace("0x", ""), 16)
        )
        if player_info.get("accent_color")
        else discord.Color.yellow(),
    )

    embed.set_author(name=player_info.get("username", "Unknown"), icon_url=player_info.get("profile_picture", ""))

    resolved_is_user = resolved_user_id is not None
    if unregistered:
        resolved_is_user = False
    resolved_id = resolved_user_id if resolved_is_user else resolved_profile_id

    id_label = "User" if resolved_is_user else "Profile"
    page_text = "[User Page]" if resolved_is_user else "[Profile Page]"
    page_url = (
        f"https://globalstatsviewer.com/users/{resolved_id}"
        if resolved_is_user
        else f"https://globalstatsviewer.com/profiles/{resolved_id}"
    )
    registered_text = f"Registered {emotes['check']}" if resolved_is_user else ""

    header_value = f"{emotes['gsv']} {page_text}({page_url})\n{registered_text}"

    embed.add_field(
        name=f"{id_label} ID: `{resolved_id if resolved_id is not None else id}`",
        value=header_value,
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
        socials_list.append(f"{emotes['youtube']} [YouTube]({socials['youtube']})")
    if socials.get("twitter"):
        socials_list.append(f"{emotes['twitter']} [Twitter]({socials['twitter']})")
    if socials.get("twitch"):
        socials_list.append(f"{emotes['twitch']} [Twitch]({socials['twitch']})")
    if socials.get("geometry_dash"):
        socials_list.append(
            f"{emotes['gd-browser']} [GDBrowser](https://gdbrowser.com/u/{socials['geometry_dash']})"
        )
    if socials.get("aredl"):
        socials_list.append(
            f"{emotes['aredl']} [AREDL](https://aredl.net/profiles/{socials['aredl']})"
        )
    if socials.get("pointercrate"):
        socials_list.append(
            f"{emotes['pointercrate']} [Pointercrate](https://pointercrate.com/demonlist/statsviewer/?player={socials['pointercrate']})"
        )
    if socials.get("pemonlist"):
        socials_list.append(
            f"{emotes['pemonlist']} [Pemonlist](https://globalstatsviewer.com/pemonlist/{socials['pemonlist']})"
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


# /completions ~~ Lets the user view completions of any searched profile, can be toggled to be Classic or Platformer completions
@tree.command(name="completions", description="Displays a user completions")
@app_commands.describe(
    id="ID of user",
    source="Lookup source",
    gamemode="Show platformer/classic completions?"
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
    ]
)
async def completions(
    interaction: discord.Interaction,
    id: str,
    source: app_commands.Choice[str],
    gamemode: app_commands.Choice[str],
):
    await interaction.response.defer()

    source_value = getattr(source, "value", str(source))
    registered = source_value == "gsv_registered"
    unregistered = source_value == "gsv_unregistered"
    lookup_type = None if (registered or unregistered) else source_value

    if registered:
        user_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(id)}"
    elif unregistered:
        user_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getprofilebasicinfo/{str(id)}"
    else:
        user_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(id)}?type={source_value}"
    
    try:
        user_response = requests.get(user_api_url)
        user_response.raise_for_status()
        user_data_raw = user_response.json()
        
        player_info = user_data_raw.get("player_info", {})

        user_data = {
            "username": player_info.get("username", "Unknown"),
            "pfp": player_info.get("profile_picture", "")
        }

        resolved_user_id, resolved_profile_id = resolve_user_profile_ids(user_data_raw)

    except requests.exceptions.RequestException as e:
        print("Error fetching user data:", e)
        await interaction.followup.send("Error fetching user data. Please try again.")
        return

    resolved_is_user = resolved_user_id is not None
    if unregistered:
        resolved_is_user = False
    resolved_id = resolved_user_id if resolved_is_user else resolved_profile_id
    user_url = (
        f"https://globalstatsviewer.com/users/{resolved_id if resolved_id is not None else id}"
        if resolved_is_user
        else f"https://globalstatsviewer.com/profiles/{resolved_id if resolved_id is not None else id}"
    )
    
    mode = getattr(gamemode, "value", str(gamemode)).lower()
    if registered:
        api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getusercompletions/{id}?type={mode}"
    elif unregistered:
        api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getprofilecompletions/{id}?type={mode}"
    else:
        api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getusercompletions/{id}?type={mode}&completions_type={lookup_type}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        completions_data = data.get("demonlist", [])
        user_accent_color = data.get("user_accent_color")
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        await interaction.followup.send("Error fetching completions data. Please try again.")
        return
    
    platformer = mode == "platformer"
    max_pages = (max(len(completions_data), 1) - 1) // 8
    page = 0
    def build_embed(page: int) -> discord.Embed:
        embed_color = discord.Color.green()
        if user_accent_color:
            try:
                embed_color = discord.Color(int(user_accent_color.replace("#", ""), 16))
            except ValueError:
                pass
        
        embed = discord.Embed(title=f"{user_data['username']}", url=user_url, color=embed_color)
        embed.set_author(name=user_data["username"], icon_url=user_data["pfp"])
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
                level_emote = f"{emotes['youtube']}"
            else:
                gddp_tier = level.get("gddp_tier", {})
                tier_name = gddp_tier.get("name")
                emote = gddp_emote_for_tier(tier_name) if tier_name else ""
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


# Run -----------------------------------------------------------------------------------------------


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await tree.sync()
    print("Slash commands synced.")


if (
    IS_DEV_ENV == DEV_STATUS.PRODUCTION
):  # Will run on test bot's token, otherwise will use ENV file
    client.run(PROD_TOKEN)
elif IS_DEV_ENV == DEV_STATUS.LOCAL_BOT:
    client.run(LOCAL_TOKEN)