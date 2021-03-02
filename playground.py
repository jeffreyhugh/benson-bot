import asyncio
import os
import threading

import discord
from discord.ext import commands
import re
import docker


def get_logs_from_container(container, save_name):
    container.wait()

    output = container.logs()

    with open("playground/{}.log".format(save_name), mode="wb") as f:
        f.write(output)


class Playground(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dockerHost = docker.from_env()
        self.cseguild = 573576119819829249

    @commands.command(name="exec", aliases=["execute", "eval", "evaluate"])
    @commands.max_concurrency(1, commands.BucketType.user, wait=False)
    async def _exec(self, ctx):
        """Execute a code snippet and post the result. Supports Python, C, Go, and Bash.

        To differentiate between languages, use a syntax-highlighted code block. In Discord, that's three backticks (`) and the language, then a newline.

        https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-"""
        async with ctx.typing():
            code = ""
            lang = ""
            regexes = ["```(?:python|py)([\s\S]*?)```", "```(?:c)([\s\S]*?)```", "```(?:golang|go)([\s\S]*?)```",
                       "```(?:bash|sh)([\s\S]*?)```", "```(?:zsh)([\s\S]*?)```"]
            langs = ["py", "c", "go", "bash", "zsh"]
            i = 0
            while i < len(regexes):
                r = re.compile(regexes[i])
                match = r.search(ctx.message.content)
                if match:
                    code = match.group(1)
                    lang = langs[i]
                    break

                i += 1

            if lang == "" or code == "":
                await ctx.message.add_reaction("❌")
                await ctx.send("Unknown language. Please use a formatted code block (e.g. ` ```c`).")
                return

            await ctx.message.add_reaction("⏳")

            os.makedirs("playground", exist_ok=True)
            with open("playground/{}.{}".format(ctx.message.id, lang), mode="w") as f:
                f.write(code)

            # Build and start container
            try:
                self.dockerHost.images.build(path="./",
                                             dockerfile="dockerfiles/{}-Dockerfile".format(lang),
                                             buildargs={"MESSAGE_ID": str(ctx.message.id)},
                                             tag="benson/" + str(ctx.message.id),
                                             forcerm=True)
            except docker.errors.BuildError:
                await ctx.message.remove_reaction("⏳", ctx.guild.me)
                await ctx.message.add_reaction("❌")
                await ctx.send("Your code failed to compile. Please double-check syntax and try again.")

                os.remove("playground/{}.{}".format(ctx.message.id, lang))
                return

            container = self.dockerHost.containers.run("benson/" + str(ctx.message.id),
                                                       name=str(ctx.message.id),
                                                       auto_remove=False,
                                                       stdout=True,
                                                       stderr=True,
                                                       detach=True,
                                                       cpu_shares=1000,  # default 1024, make it lower priority
                                                       mem_limit="512m")

            t = threading.Thread(target=get_logs_from_container,
                                 name=str(ctx.message.id),
                                 args=(container, ctx.message.id))
            t.daemon = True
            t.start()

            os.remove("playground/{}.{}".format(ctx.message.id, lang))

            time_running = 0
            was_killed = False

            while not os.path.exists("playground/{}.log".format(ctx.message.id)):
                await asyncio.sleep(1)
                time_running += 1
                if time_running > 45:
                    container.kill()
                    was_killed = True
                    break

            if was_killed:
                await ctx.message.remove_reaction("⏳", ctx.guild.me)
                await ctx.message.add_reaction("❌")
                await ctx.send("<@{}> Your program was terminated because it took too long".format(ctx.author.id))
            else:
                with open("playground/{}.log".format(ctx.message.id)) as f:
                    output = f.read()
                await ctx.message.remove_reaction("⏳", ctx.guild.me)
                await ctx.message.add_reaction("✅")
                msg = await ctx.send("<@{}> ```{}```".format(ctx.author.id, output[0:800]),
                               file=discord.File("playground/{}.log".format(ctx.message.id)))
                await msg.add_reaction("🗑️")

            try:
                os.remove("playground/{}.log".format(ctx.message.id))
            except FileNotFoundError:
                pass

        return

    @_exec.error
    async def _exec_error(self, ctx, error):
        if isinstance(error, commands.errors.MaxConcurrencyReached):
            await ctx.message.add_reaction("❌")
            await ctx.send("You may only run one instance of this command at a time.")
        else:
            raise error

    @commands.Cog.listener("on_raw_reaction_add")
    async def _on_raw_reaction_add(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        if channel is not None:
            message = channel.get_partial_message(payload.message_id)
        else:
            # DM
            return

        user_id = payload.user_id
        emoji = payload.emoji

        if guild.id != self.cseguild:
            return

        if emoji.name != "🗑️":  # Wastebasket
            return

        message = await message.fetch()  # Convert from partial message to message
        if message.author.id != guild.me.id:
            return

        target = await guild.fetch_member(user_id)
        if target is None:
            return

        if target in message.mentions:
            await message.edit(content="<@{}> [redacted]".format(target.id))

        return
