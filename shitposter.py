import re

from discord.ext import commands


class Shitposter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.benson = "https://cdn.discordapp.com/attachments/612329169011081219/750120697556238387/benson.jpg"
        self.meme_channels = [612019519673597962, 612329169011081219, 621180351573917712, 614623979898011659,
                              613137801629794394, 510109263809740800]
        self.general_channel = 612329169011081219
        self.botspam = 758793612229083178
        self.arch_emoji = "<:arch:744787585779630171>"
        self.benson_emoji = "<:benson:827281034609164288>"

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        print("{} is now logged in and ready".format(self.bot.user))

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            # if "benson" in message.content.lower() and (message.channel.id in self.meme_channels or message.guild is None):
            #    await message.channel.send(benson, delete_after=10)

            benson_regex = re.compile(r"\bbenson\b", re.IGNORECASE)
            if len(benson_regex.findall(message.content)) != 0 and (
                    message.channel.id in self.meme_channels or message.guild is None):
                await message.add_reaction(self.benson_emoji)

            arch_regex = re.compile(r"\barch linux\b", re.IGNORECASE)
            if len(arch_regex.findall(message.content)) != 0 and (
                    message.channel.id in self.meme_channels or message.guild is None):
                await message.add_reaction(self.arch_emoji)

        # await self.bot.process_commands(message)
