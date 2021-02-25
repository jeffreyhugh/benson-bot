import os

import discord
from discord.ext import commands
import re
import docker
import tarfile


class Playground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dockerHost = docker.from_env()

    @commands.Command(name="py", aliases=["python"])
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def _py(self, ctx):
        """Execute a Python snippet and post the result."""
        async with ctx.typing():
            code = ""

            r = re.compile("```py(.*?)```")
            match = r.search(ctx.message.content)
            if match:
                code = match.group(1)
            else:
                await ctx.send("Invalid syntax. Please use a Python code block (` ```py`).")
                return

            os.makedirs("playground", exist_ok=True)
            with open("playground/{}.py".format(ctx.message.id), mode="w") as f:
                f.write(code)
            with tarfile.open("playground/{}.tar".format(ctx.message.id), mode="w") as tar:
                tar.add("playground/{}.py".format(ctx.message.id))

            data = open("playground/{}.py".format(ctx.message.id), "rb").read()

            # Start container
            container = self.dockerHost.containers.create("python:3.9.2-alpine3.13", name=str(ctx.message.id))
            container.put_archive("/tmp", data)

            # Returns tuple of exit_code, output
            exit_and_output = container.exec_run(["timeout", "60s", "python3.8", "{}.py".format(ctx.message.id)])

            # Cleanup
            container.remove()

            with open("playground/{}.out".format(ctx.message.id), mode="w") as f:
                f.write(exit_and_output[1])
                await ctx.send("exit {}: ```\n{}```".format(exit_and_output[0], exit_and_output[1][0:800]), file=f)
