import asyncio
import os
import threading
import time

import discord
from discord.ext import commands
import re
import docker
import tarfile


def get_logs_from_container(container, save_name):
    container.wait()

    output = container.logs()

    with open("playground/{}.out".format(save_name), mode="wb") as f:
        f.write(output)


class Playground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dockerHost = docker.from_env()

    @commands.command(name="py", aliases=["python"])
    @commands.max_concurrency(1, commands.BucketType.user, wait=False)
    async def _py(self, ctx):
        """Execute a Python snippet and post the result."""
        async with ctx.typing():
            r = re.compile("```(?:python|py)([^.]*?)```")
            match = r.search(ctx.message.content)
            if match:
                code = match.group(1)
            else:
                await ctx.message.add_reaction("❌")
                await ctx.send("Invalid syntax. Please use a Python code block (` ```py`).")
                return

            await ctx.message.add_reaction("⏳")

            os.makedirs("playground", exist_ok=True)
            with open("playground/{}.py".format(ctx.message.id), mode="w") as f:
                f.write(code)

            exited_with_error = False

            # Build and start container
            self.dockerHost.images.build(path="./",
                                         dockerfile="dockerfiles/python-Dockerfile",
                                         buildargs={"MESSAGE_ID": str(ctx.message.id)},
                                         tag="benson/" + str(ctx.message.id),
                                         forcerm=True)

            container = self.dockerHost.containers.run("benson/" + str(ctx.message.id),
                                                       name=str(ctx.message.id),
                                                       auto_remove=False,
                                                       stdout=True,
                                                       stderr=True,
                                                       detach=True,
                                                       cpu_shares=1000,  # def. 1024, this should make it low priority
                                                       mem_limit="512m",
                                                       storage_opt={"size": "1G"})

            t = threading.Thread(target=get_logs_from_container,
                                 name=str(ctx.message.id),
                                 args=(container, ctx.message.id))
            t.daemon = True
            t.start()

            os.remove("playground/{}.py".format(ctx.message.id))

            while not os.path.exists("playground/{}.out".format(ctx.message.id)):
                await asyncio.sleep(1)

            with open("playground/{}.out".format(ctx.message.id)) as f:
                output = f.read()

            await ctx.send("<@{}> ```{}```".format(ctx.author.id, output[0:800]),
                           file=discord.File("playground/{}.out".format(ctx.message.id)))

            os.remove("playground/{}.out".format(ctx.message.id))

        return

    @_py.error
    async def _py_error(self, ctx, error):
        if isinstance(error, commands.errors.MaxConcurrencyReached):
            await ctx.message.add_reaction("❌")
            await ctx.send("You can only run one instance of this command at a time.")
        else:
            raise error
