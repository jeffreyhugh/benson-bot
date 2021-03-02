import os

from discord.ext import commands


def main():
    bot = commands.Bot(command_prefix=commands.when_mentioned_or("!!"))

    env = os.getenv("BENSONBOT_ENV_TYPE")
    if env == "MAIN":
        from duty_manager import DutyManager
        from memeail import ProblemOfTheDay
        from shitposter import Shitposter
        from ticker import Ticker
        from timers import CSE107Timer, CSE113Timer
        from message_scheduler import MessageScheduler

        bot.add_cog(CSE113Timer(bot))
        bot.add_cog(CSE107Timer(bot))
        bot.add_cog(DutyManager(bot))
        bot.add_cog(MessageScheduler(bot))

        bot.add_cog(ProblemOfTheDay(bot))

        bot.add_cog(Shitposter(bot))
        bot.add_cog(Ticker(bot))

    elif env == "PLAYGROUND":
        from playground import Playground

        bot.add_cog(Playground(bot))

    else:
        print("Unknown environment ({})".format(env))
        return

    bot.run(os.getenv("BENSONBOT_DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
