import os

import discord
from discord.ext import commands

from playground import Playground


def main():
    intents = discord.Intents.none()
    intents.messages = True
    intents.reactions = True
    intents.guilds = True
    #intents.members = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!!"), intents=intents)

    # Utility
    bot.add_cog(Playground(bot))

    bot.run(os.getenv("BENSONBOT_DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
