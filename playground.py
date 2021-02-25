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

    @commands.command(name="py", aliases=["python"])
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def _py(self, ctx):
        """Execute a Python snippet and post the result."""
        async with ctx.typing():
            code = ""

            r = re.compile("```(?:py|python)([^.]*?)```")
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

            data = open("playground/{}.tar".format(ctx.message.id), "rb").read()

            # Build and start container
            image = self.dockerHost.images.build(path="./",
                                                 dockerfile="dockerfiles/python-Dockerfile",
                                                 buildargs={"MESSAGE_ID": str(ctx.message.id)},
                                                 tag="benson/" + str(ctx.message.id),
                                                 forcerm=True)
            output = self.dockerHost.containers.run("benson/" + str(ctx.message.id),
                                                    name=str(ctx.message.id),
                                                    auto_remove=True)

            # container.put_archive("/tmp", data)

            # Returns tuple of exit_code, output
            #while True:
            #    try:
            #        exit_and_output = container.exec_run(["python3", "/tmp/{}.py".format(ctx.message.id)])
            #    except docker.errors.APIError:
            #        continue
            #    finally:
            #        break


            # Cleanup
            #container.kill()
            #container.remove()
            os.remove("playground/{}.*".format(ctx.message.id))

            with open("playground/{}.out".format(ctx.message.id), mode="wb") as f:
                f.write(output)
                await ctx.send("__**Python 3.9**__ ```{}```".format(bytes.decode(output)), file=discord.File("playground/{}.out".format(ctx.message.id)))
