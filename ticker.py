import discord
from discord.ext import commands, tasks


class Ticker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.ticker_messages = ["TAs: use !!offduty", "no proposal, no waifu", "Benson is cool"]
        self.original_messages = self.ticker_messages

        self.ticker_loop.start()

    @tasks.loop(seconds=20)
    async def ticker_loop(self):
        await self.bot.change_presence(
            activity=discord.Game(self.ticker_messages[self.index % len(self.ticker_messages)]))
        if self.index % len(self.ticker_messages) == 0:
            self.index = 0
        self.index += 1

    @ticker_loop.before_loop
    async def before_ticker_loop(self):
        await self.bot.wait_until_ready()

    @commands.command(name="tickeradd")
    async def _tickeradd(self, ctx, message):
        """Add a message to the ticker. The message is volatile and will be erased on next start-up."""
        self.ticker_messages.append(message)
        await ctx.message.add_reaction("✅")

    @commands.command(name="tickerpurge")
    async def _tickerpurge(self, ctx):
        """Reset the ticker to the messages in the code."""
        self.index = 0
        self.ticker_messages = self.original_messages
        await ctx.message.add_reaction("✅")
