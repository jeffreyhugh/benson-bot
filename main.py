import os

from discord.ext import commands

from duty_manager import DutyManager
from memeail import ProblemOfTheDay
from shitposter import Shitposter
from ticker import Ticker
from timers import CSE107Timer, CSE113Timer


def main():
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!!"))

    # Utility
    bot.add_cog(CSE113Timer(bot))
    bot.add_cog(CSE107Timer(bot))
    bot.add_cog(DutyManager(bot))

    # Professional
    bot.add_cog(ProblemOfTheDay(bot))

    # Kevin-tier
    bot.add_cog(Shitposter(bot))
    bot.add_cog(Ticker(bot))

    bot.run(os.getenv("BENSONBOT_DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
