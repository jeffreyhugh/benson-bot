import os

import discord
from discord.ext import commands

from duty_manager import DutyManager
from memeail import ProblemOfTheDay
from shitposter import Shitposter
from ticker import Ticker
from timers import CSE107Timer, CSE113Timer
from message_scheduler import MessageScheduler


def main():
    intents = discord.Intents.none()
    intents.messages = True
    intents.reactions = True
    intents.members = True
    intents.guilds = True

    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!!"), intents=intents)

    # Utility
    bot.add_cog(CSE113Timer(bot))
    bot.add_cog(CSE107Timer(bot))
    bot.add_cog(DutyManager(bot))
    bot.add_cog(MessageScheduler(bot))

    # Professional
    bot.add_cog(ProblemOfTheDay(bot))

    # Kevin-tier
    bot.add_cog(Shitposter(bot))
    bot.add_cog(Ticker(bot))

    bot.run(os.getenv("BENSONBOT_DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
