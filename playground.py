import discord
from discord.ext import commands
import re
import docker

class Playground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.docker = docker.from_env()

    @commands.Command(name="py", aliases=["python"])
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def _py(self, ctx):
        """Execute a small Python script and post the result to chat."""
        code = ""

        r = re.compile("```py(.*?)```")
        match = r.search(ctx.message.content)
        if match:
            code = match.group(1)
        else:
            await ctx.send("Invalid syntax. Please use a Python codeblock (` ```py`).")
            return

        with open("{}.py".format(ctx.message.id), "w") as f:
            f.write(code)

        # Start container

