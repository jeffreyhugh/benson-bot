from discord.ext import commands


class Shitposter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.benson = "https://cdn.discordapp.com/attachments/612329169011081219/750120697556238387/benson.jpg"
        self.meme_channels = [612019519673597962, 612329169011081219, 621180351573917712, 614623979898011659,
                              613137801629794394]
        self.general_channel = 612329169011081219
        self.botspam = 758793612229083178
        self.arch_emoji = "<:arch:744787585779630171>"

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        print("{} is now logged in and ready".format(self.bot.user))

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            # if "benson" in message.content.lower() and (message.channel.id in self.meme_channels or message.guild is None):
            #    await message.channel.send(benson, delete_after=10)

            if "arch linux" in message.content.lower() and (
                    message.channel.id in self.meme_channels or message.guild is None):
                await message.add_reaction(self.arch_emoji)

        await self.bot.process_commands(message)
