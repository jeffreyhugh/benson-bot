import asyncio

from discord.ext import commands
from pytimeparse import parse


async def is_manager(ctx):
    for r in ctx.author.roles:
        if r.name == "BotAdmin":
            return True


async def can_use_onduty(ctx):
    for r in ctx.author.roles:
        if r.name in ["BotAdmin", "Grutor113", "Grutor107", "Tutor", "TA"]:
            return True
    return False


class DutyManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cseguild = 573576119819829249
        self.role_helpme = 751581791147524119

    @commands.command(name="onduty")
    @commands.check(can_use_onduty)
    async def _on_duty(self, ctx, time=""):
        '''Allows TAs, grutors, and general tutors to mark themselves as on-duty. BotAdmins can mark others as on-duty.'''
        if time == "":
            await ctx.send("Please provide a time argument with this command. For help, type `!!help`.")
            return
        seconds = parse(time)
        helpmerole = self.bot.get_guild(self.cseguild).get_role(self.role_helpme)
        manager = await is_manager(ctx)
        if manager and len(ctx.message.mentions) != 0:
            for m in ctx.message.mentions:
                await m.add_roles(helpmerole)
        else:
            await ctx.author.add_roles(helpmerole)

        await ctx.message.add_reaction("✅")

        await asyncio.sleep(seconds)

        if manager and len(ctx.message.mentions) != 0:
            for m in ctx.message.mentions:
                await m.remove_roles(helpmerole)
        else:
            await ctx.author.remove_roles(helpmerole)

    @_on_duty.error
    async def _on_duty_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")

    @commands.command(name="offduty")
    @commands.check(can_use_onduty)
    async def _off_duty(self, ctx):
        """If automatic role removal fails, use this command."""
        helpmerole = self.bot.get_guild(self.cseguild).get_role(self.role_helpme)
        manager = await is_manager(ctx)
        if manager and len(ctx.message.mentions) != 0:
            for m in ctx.message.mentions:
                await m.remove_roles(helpmerole)
        else:
            await ctx.author.remove_roles(helpmerole)

        await ctx.message.add_reaction("✅")

    @_off_duty.error
    async def _off_duty_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
