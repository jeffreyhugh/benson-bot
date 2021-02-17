import datetime
import sqlite3

from discord.ext import commands, tasks
from pytimeparse import parse


class MessageScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.cseguild = 573576119819829249
        self.generalchannel = 612329169011081219

        self.conn = sqlite3.connect("hamdy.db")
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY,
                        send_at FLOAT NOT NULL,
                        message TEXT NOT NULL,
                        target_channel TEXT,
                        finished INTEGER DEFAULT 0)''')

    @commands.command(name="schedule-with-delta")
    @commands.is_owner()
    async def _schedule_with_delta(self, ctx, delta="", target="", message=""):
        """Schedule a message to be sent at some point in the future relative to the current time."""
        if delta == 0 or target == 0 or message == "":
            await ctx.send("Missing one or more required arguments. For help, type `!!help`")
            return
        now = datetime.datetime.now()
        plusdelta = (now + datetime.timedelta(seconds=parse(delta))).timestamp()
        self.c.execute('''INSERT INTO messages 
                        (send_at, message, target_channel)
                        VALUES(?, ?, ?)''', (plusdelta, message, str(ctx.channel.id)))
        self.conn.commit()

        await ctx.message.add_reaction("✅")

    @_schedule_with_delta.error
    async def _schedule_with_delta_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise err

    @commands.command(name="schedule-at")
    @commands.is_owner()
    async def _schedule_at(self, ctx, t="", target="", message=""):
        """Schedule a message to be sent at some point in the future."""
        if t == "" or target == 0 or message == "":
            await ctx.send("Missing one or more required arguments. For help, type `!!help`")
            return

        try:
            targs = t.split("@")
            hms = targs[1]
            mdy = targs[0]

            dateargs = mdy.split("/")
            month = int(dateargs[0])
            day = int(dateargs[1])
            year = int(dateargs[2])

            timeargs = hms.split(":")
            hours = int(timeargs[0])
            minutes = int(timeargs[1])
            seconds = int(timeargs[2])
        except IndexError:
            await ctx.message.add_reaction("❌")
            return

        now = datetime.datetime(year=year, month=month, day=day, hour=hours, minute=minutes, second=seconds).timestamp()

        self.c.execute('''INSERT INTO messages 
                        (send_at, message, target_channel)
                        VALUES(?, ?, ?)''', (now, message, str(ctx.channel.id)))
        self.conn.commit()

        await ctx.message.add_reaction("✅")

    @_schedule_at.error
    async def _schedule_at_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise err

    @tasks.loop(minutes=5.0)
    async def check_for_messages(self):
        now = datetime.datetime.now().timestamp()
        self.c.execute('''SELECT id, target_channel, message FROM messages WHERE finished = 0 AND send_at < ?''', [now])
        messages = self.c.fetchall()
        # [id, channel id, message content]
        #   0      1              2

        for m in messages:
            chan = self.bot.get_guild(self.cseguild).get_channel(int(m[1]))
            if chan is None:
                continue

            chan.send(m[2])

            self.c.execute('''UPDATE messages
                            SET finished=1
                            WHERE id=?''', [m[0]])
            self.conn.commit()

    @check_for_messages.before_loop
    async def before_check_for_messages(self):
        await self.bot.wait_until_ready()
