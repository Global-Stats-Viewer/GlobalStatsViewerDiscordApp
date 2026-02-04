# config.py
# -- Global Constants & Dev. Configs

from enum import Enum
from dotenv import load_dotenv
import json
import os

# -------------------------------------------------------------


class DEV_STATUS(Enum):
    PRODUCTION = 0
    LOCAL_BOT = 1


# 0 - For production // 1 - For Local BOT
IS_DEV_ENV = DEV_STATUS.LOCAL_BOT
IS_DEV_API = DEV_STATUS.PRODUCTION

BOT_VERSION = "v1.1.0"

# >> TOKEN SETTING

LOCAL_TOKEN = None
PROD_TOKEN = None
PREFIX = None

APP_ID = 1424406048256692446 if IS_DEV_ENV == DEV_STATUS.LOCAL_BOT else 1437182190818431067
# emotes

EMOTES: dict[str, dict[str, str]] = {
    "dev": {
        "gsv": "<:Logogsv:1431369691028263012>",
        "ul": "<:ULLogoNew:1431382668867801160>",
        "gd-browser": "<:gdbrowser:1431369804253757440>",
        "aredl": "<:aredl:1431369774050447431>",
        "pointercrate": "<:Demon_List_Logo:1431382605906968636>",
        "pemonlist": "<:pemonlist:1431370025180070020>",
        "gddp": "<:gddplogo:1431369826709930024>",
        "check": "<:check:1434616324276883601>",
        "youtube": "<:youtube:1432459558340530297>",
        "twitter": "<:twitter:1432459572509020190>",
        "twitch": "<:twitch:1432459584689410079>",
        "github": "<:github:1468335018530050048>",
        # GDDP Tier Emotes
        "platinum": "<:Platinum:1434146574921109615>",
        "sapphire": "<:Sapphire:1434146692189524158>",
        "jade": "<:Jade:1434147294030205109>",
        "emerald": "<:Emerald:1434277560061005874>",
        "ruby": "<:Ruby:1434277643339173941>",
        "diamond": "<:Diamond:1434147062731116695>",
        "pearl": "<:Pearl:1434146742345011321>",
        "onyx": "<:Onyx:1434147005298643105>",
        "amethyst": "<:Amethyst:1434146965326925824>",
        "azurite": "<:Azurite:1434146937543594085>",
        # the staff icons ig
        "dev": "<:dev:1468289746261246148>",
        "helper": "<:helper:1468289778242818343>",
        "mod": "<:mod:1468289788950876191>",
        "owner": "<:owner:1468289802318249984>",
    },
    "prod": {
        "gsv": "<:Logogsv:1437184843405328394>",
        "ul": "<:ullogo:1437185243244134550>",
        "gd-browser": "<:gdbrowser:1437184944488058980>",
        "aredl": "<:aredl:1437184917950824551>",
        "pointercrate": "<:demonlist:1437185149208100895>",
        "pemonlist": "<:pemonlist:1437185008388407497>",
        "gddp": "<:gddplogo:1437184974666338506>",
        "check": "<:check:1437185817083646023>",
        "youtube": "<:youtube:1437185337385554020>",
        "twitter": "<:twitter:1437185361213259897>",
        "twitch": "<:twitch:1437185348881879171>",
        "github": "<:github:1468334885881254171>",
        # GDDP Tier Emotes
        "platinum": "<:Platinum:1437185529505513472>",
        "sapphire": "<:Sapphire:1437185565748629757>",
        "jade": "<:Jade:1437185710334410752>",
        "emerald": "<:Emerald:1437185753770758254>",
        "ruby": "<:Ruby:1437185770451374250>",
        "diamond": "<:Diamond:1437185675538595981>",
        "pearl": "<:Pearl:1437185584434253984>",
        "onyx": "<:Onyx:1437185658136559818>",
        "amethyst": "<:Amethyst:1437185621390004285>",
        "azurite": "<:Azurite:1437185610715500797>",
        # the staff icons ig
        "dev": "<:dev:1468290442356588739>",
        "helper": "<:helper:1468290452145836102>",
        "mod": "<:mod:1468290602532732949>",
        "owner": "<:owner:1468290612024443153>",
    },
}

# >> Local BOT config

if IS_DEV_API == DEV_STATUS.LOCAL_BOT:
    PREFIX = "testapi"
elif IS_DEV_API == DEV_STATUS.PRODUCTION:
    PREFIX = "api"

LOCAL_FOLDER = ".local/"
ENV_PATH = LOCAL_FOLDER + ".env"
DOT_ENV = load_dotenv(dotenv_path=ENV_PATH)

if IS_DEV_ENV == DEV_STATUS.LOCAL_BOT:
    LOCAL_TOKEN = os.getenv("DEV_TOKEN")
elif IS_DEV_ENV == DEV_STATUS.PRODUCTION:
    PROD_TOKEN = os.getenv("PROD_TOKEN")