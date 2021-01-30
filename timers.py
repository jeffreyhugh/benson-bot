from discord.ext import commands, tasks


async def is_manager(ctx):
    for r in ctx.author.roles:
        if r.name == "BotAdmin":
            return True


class CSE113Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

        self.cseguild = 573576119819829249
        self.channel_113b = 801145102805893200
        self.channel_113s = 801144861808918559

        self.role_113b = 744744422205292595
        self.role_113s = 744744290705604671

        self.message_start = "{} begin pair programming"
        self.message_swap = "{} swap now"
        self.message_end = "{} class is over, have a good day"

    async def send_message(self, message):
        await self.bot.get_guild(self.cseguild).get_channel(self.channel_113b).send(
            message.format("<@&{}>".format(self.role_113b)))
        await self.bot.get_guild(self.cseguild).get_channel(self.channel_113s).send(
            message.format("<@&{}>".format(self.role_113s)))

    @commands.command(name="cse113")
    @commands.check(is_manager)
    async def _pair(self, ctx, action):
        '''Start, restart, cancel, or get status for the timer for the CSE113 pair programming swaps'''
        if action.lower() == "start":
            if not self.cse113_call_ten.is_running():
                self.index = 0
                self.cse113_call_ten.start()
                await ctx.message.add_reaction("✅")
            else:
                await ctx.send("This task is already running")

        elif action.lower() == "restart":
            self.index = 0
            self.cse113_call_ten.start()
            await ctx.message.add_reaction("✅")

        elif action.lower() in ["stop", "cancel"]:
            self.cse113_call_ten.cancel()
            await ctx.message.add_reaction("✅")

        elif action.lower() == "status":
            if self.cse113_call_ten.is_running():
                await ctx.send("Task is running, current iteration {}/5".format(self.index))
            elif self.cse113_call_ten.is_being_cancelled():
                await ctx.send("Task is being cancelled")
            elif self.cse113_call_ten.failed():
                await ctx.send("Task has failed")
            else:
                await ctx.send("Unknown status")

    @_pair.error
    async def _pair_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise error

    @tasks.loop(minutes=10.0, count=6)
    async def cse113_call_ten(self):
        self.index += 1
        if self.index == 1:
            await self.send_message(self.message_start)
        elif 1 < self.index < 6:
            await self.send_message(self.message_swap)
        elif self.index == 6:
            await self.send_message(self.message_end)
            self.cse113_call_ten.cancel()


class CSE107Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.index = 0

        self.cseguild = 573576119819829249
        self.channel_107 = 801147110144868362

        self.role_107 = 744744169339093043

        self.message_start = "{} begin pair programming"
        self.message_swap = "{} swap now"
        self.message_end = "{} class is over, have a good day"

    async def send_message(self, message):
        await self.bot.get_guild(self.cseguild).get_channel(self.channel_107).send(
            message.format("<@&{}>".format(self.role_107)))

    @commands.command(name="cse107")
    @commands.check(is_manager)
    async def _pair(self, ctx, action):
        '''Start, restart, cancel, or get status for the timer for the CSE107 pair programming swaps'''
        if action.lower() == "start":
            if not self.cse107_call_ten.is_running():
                self.index = 0
                self.cse107_call_ten.start()
                await ctx.message.add_reaction("✅")
            else:
                await ctx.send("This task is already running")

        elif action.lower() == "restart":
            self.index = 0
            self.cse107_call_ten.start()
            await ctx.message.add_reaction("✅")

        elif action.lower() in ["stop", "cancel"]:
            self.cse107_call_ten.cancel()
            await ctx.message.add_reaction("✅")

        elif action.lower() == "status":
            if self.cse107_call_ten.is_running():
                await ctx.send("Task is running, current iteration {}/5".format(self.index))
            elif self.cse107_call_ten.is_being_cancelled():
                await ctx.send("Task is being cancelled")
            elif self.cse107_call_ten.failed():
                await ctx.send("Task has failed")
            else:
                await ctx.send("Unknown status")

    @_pair.error
    async def _pair_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise error

    @tasks.loop(minutes=10.0, count=6)
    async def cse107_call_ten(self):
        self.index += 1
        if self.index == 1:
            await self.send_message(self.message_start)
        elif 1 < self.index < 6:
            await self.send_message(self.message_swap)
        elif self.index == 6:
            await self.send_message(self.message_end)
            self.cse107_call_ten.cancel()
