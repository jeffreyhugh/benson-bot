import datetime
import sqlite3
import asyncio

import discord
from discord.ext import commands, tasks
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
        self.digestchannel = 797186419142557737

        self.conn = sqlite3.connect("hamdy.db")
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS duty (
                        id INTEGER PRIMARY KEY, 
                        member_id TEXT NOT NULL, 
                        on_duty_at FLOAT, 
                        off_duty_at FLOAT, 
                        actual_off_duty FLOAT, 
                        marked_by TEXT, 
                        link TEXT NOT NULL)''')

        self.refresh_duty.start()
        self.daily_digest.start()

    @commands.command(name="onduty")
    @commands.check(can_use_onduty)
    async def _on_duty(self, ctx, time=""):
        """Allows TAs, grutors, and general tutors to mark themselves as on-duty. BotAdmins can mark others as on-duty."""
        if time == "":
            await ctx.send("Please provide a time argument with this command. For help, type `!!help`.")
            return
        seconds = parse(time)
        helpmerole = self.bot.get_guild(self.cseguild).get_role(self.role_helpme)
        manager = await is_manager(ctx)
        if manager and len(ctx.message.mentions) != 0:
            for m in ctx.message.mentions:
                await m.add_roles(helpmerole)

                member_id = str(m.id)
                now = datetime.datetime.now()
                off = now + datetime.timedelta(seconds=seconds)
                now = now.timestamp()
                off = off.timestamp()
                marked_by = str(ctx.author.id)
                link = ctx.message.jump_url
                self.c.execute('''INSERT INTO duty 
                                (member_id, on_duty_at, off_duty_at, marked_by, link) 
                                VALUES(?, ?, ?, ?, ?)''', (member_id, now, off, marked_by, link))
                self.conn.commit()
        else:
            await ctx.author.add_roles(helpmerole)

            member_id = str(ctx.author.id)
            now = datetime.datetime.now()
            off = now + datetime.timedelta(seconds=seconds)
            now = now.timestamp()
            off = off.timestamp()
            link = ctx.message.jump_url

            self.c.execute('''INSERT INTO duty
                            (member_id, on_duty_at, off_duty_at, link)
                            VALUES(?, ?, ?, ?)''', (member_id, now, off, link))
            self.conn.commit()

        await ctx.message.add_reaction("✅")

    @_on_duty.error
    async def _on_duty_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise err

    @commands.command(name="offduty")
    @commands.check(can_use_onduty)
    async def _off_duty(self, ctx):
        """If automatic role removal fails, use this command."""
        helpmerole = self.bot.get_guild(self.cseguild).get_role(self.role_helpme)
        manager = await is_manager(ctx)
        if manager and len(ctx.message.mentions) != 0:
            for m in ctx.message.mentions:
                await m.remove_roles(helpmerole)

                member_id = str(m.id)
                now = datetime.datetime.now().timestamp()

                self.c.execute('''UPDATE duty
                                SET actual_off_duty=?
                                WHERE member_id=?''', (now, member_id))
                self.conn.commit()
        else:
            await ctx.author.remove_roles(helpmerole)

            member_id = str(ctx.author.id)
            now = datetime.datetime.now().timestamp()

            self.c.execute('''UPDATE duty
                            SET actual_off_duty=?
                            WHERE member_id=?''', (now, member_id))
            self.conn.commit()

        await ctx.message.add_reaction("✅")

    @_off_duty.error
    async def _off_duty_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise err

    @tasks.loop(minutes=1.0)
    async def refresh_duty(self):
        """Responsible for automatically removing the HelpMe role"""
        now = datetime.datetime.now().timestamp()
        self.c.execute('''SELECT ID FROM duty WHERE actual_off_duty IS NULL AND off_duty_at < ?''', [now])
        all_offduty = self.c.fetchall()

        helpmerole = self.bot.get_guild(self.cseguild).get_role(self.role_helpme)

        for thing in all_offduty:
            id = thing[0]
            self.c.execute('''UPDATE duty
                            SET actual_off_duty=?
                            WHERE id=?''', (now, id))
            self.conn.commit()
            self.c.execute('''SELECT member_id FROM duty WHERE id=?''', [id])
            member_id = self.c.fetchone()[0]

            g = self.bot.get_guild(self.cseguild)
            m = await g.fetch_member(member_id)
            if m is not None:
                await m.remove_roles(helpmerole)

    @refresh_duty.before_loop
    async def before_refresh_duty(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def daily_digest(self):
        """Send a daily digest of who all marked themselves on-duty"""
        print("Sending daily duty digest at {}".format(datetime.datetime.now()))
        prev24 = (datetime.datetime.now() - datetime.timedelta(hours=24.0)).timestamp()
        self.c.execute('''SELECT * FROM duty WHERE on_duty_at > ?''', [prev24])
        all_onduty = self.c.fetchall()
        # [id, member_id, on_duty_at, off_duty_at, actual_off_duty, marked_by, link]
        #   0      1          2             3            4              5        6

        e = discord.Embed(title="Daily Duty Digest (past 24 hours)", description="", color=discord.Color(16712762))
        for thing in all_onduty:
            if thing[5] is not None:
                remark = "<@{}> was marked on-duty by <@{}> at {} for {} minutes and was marked off-duty at {} [link]({})\n".format(
                    thing[1], thing[5], datetime.datetime.fromtimestamp(thing[2]).strftime("%H:%M"),
                    (thing[3] - thing[2]) / 60, datetime.datetime.fromtimestamp(thing[4]).strftime("%H:%M"), thing[6])
            else:
                remark = "<@{}> was marked on-duty at {} for {} minutes and was marked off-duty at {} [link]({})\n".format(
                    thing[1], datetime.datetime.fromtimestamp(thing[2]).strftime("%H:%M"),
                    (thing[3] - thing[2]) / 60, datetime.datetime.fromtimestamp(thing[4]).strftime("%H:%M"), thing[6])

            e.description += remark

        await self.bot.get_guild(self.cseguild).get_channel(self.digestchannel).send(embed=e)

    @daily_digest.before_loop
    async def before_daily_digest(self):
        await self.bot.wait_until_ready()
        while True:
            now = datetime.datetime.now()
            if now.hour == 0:  # running on a host in ET, midnight ET = 10pm MT
                break
            await asyncio.sleep(300)
