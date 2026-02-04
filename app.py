# app.py
# -- Discord bot

from config import (
    IS_DEV_ENV,
    DEV_STATUS,
    LOCAL_TOKEN,
    PROD_TOKEN,
    APP_ID,
)

import discord
from discord.ext import commands

intents = discord.Intents.all()

class GSVBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("commands.about")
        await self.load_extension("commands.ping")
        await self.load_extension("commands.staff_list")
        await self.load_extension("commands.profile")
        await self.load_extension("commands.completions")


client = GSVBot(command_prefix=lambda bot, msg: [], intents=intents, application_id=APP_ID)
tree = client.tree

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