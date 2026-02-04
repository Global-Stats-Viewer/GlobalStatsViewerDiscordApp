import requests
import discord
from typing import Any, Dict, Optional, Tuple
from config import EMOTES, IS_DEV_ENV, DEV_STATUS, PREFIX


emotes = EMOTES["dev"] if IS_DEV_ENV == DEV_STATUS.LOCAL_BOT else EMOTES["prod"]


staff_flags = {
    "OWNER": 1,
    "ADMIN": 2,
    "DEVELOPER": 4,
    "MODERATOR": 8,
    "HELPER": 16,
}


def gddp_emote_for_tier(tier_name: str) -> str:
    try:
        if not tier_name:
            return ""
        return emotes.get(tier_name.lower(), "")
    except Exception:
        return ""
    
    
def has_role(staff_type: int, role: int) -> bool:
    return (staff_type & role) == role


def format_staff_user(user: Dict[str, Any]) -> str:
    username = user.get("username", "Unknown")
    user_id = user.get("id")
    if user_id is None:
        return str(username)
    return f"[{username}](https://globalstatsviewer.com/users/{user_id})"


def fetch_both_ways_info(user_id: str, source_value: str):
    user_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getuserbasicinfo/{str(user_id)}?type={source_value}"
    profile_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getprofilebasicinfo/{str(user_id)}?type={source_value}"
    try:
        response = requests.get(user_api_url)
        response.raise_for_status()
        data = response.json()
        return data, True
    except requests.exceptions.RequestException as e:
        try:
            response = requests.get(profile_api_url)
            response.raise_for_status()
            data = response.json()
            return data, False
        except requests.exceptions.RequestException as e:
            print(e)
            return ""


async def fetch_json(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
    

def fetch_both_ways_comp(user_id: str, mode: str, source_value: str):
    user_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getusercompletions/{user_id}?type={mode}&completions_type={source_value}"
    profile_api_url = f"https://{PREFIX}.globalstatsviewer.com/api/getprofilecompletions/{user_id}?type={mode}&completions_type={source_value}"
    try:
        response = requests.get(user_api_url)
        response.raise_for_status()
        data = response.json()
        return data, True
    except requests.exceptions.RequestException as e:
        try:
            response = requests.get(profile_api_url)
            response.raise_for_status()
            data = response.json()
            return data, False
        except requests.exceptions.RequestException as e:
            print(e)
            return ""