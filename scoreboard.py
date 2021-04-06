import datetime
import sqlite3

import discord
import pytz
from discord.ext import commands


async def is_manager(ctx):
    for r in ctx.author.roles:
        if r.name == "BotAdmin":
            return True


class Scoreboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cseguild = 453071081432023042
        self.sections = {"blue": 510109263809740800,
                         "silver": 828876182413770763}
        self.tz = pytz.timezone("America/Denver")

        self.conn = sqlite3.connect("hamdy.db")
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS scoreboard_teams (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        section TEXT NOT NULL,
                        score INTEGER DEFAULT 0)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS scoreboard_members (
                        id INTEGER PRIMARY KEY,
                        member_id TEXT NOT NULL,
                        belongs_to INTEGER,
                        FOREIGN KEY(belongs_to) REFERENCES scoreboard_teams(id))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS scoreboard_messages (
                        id INTEGER PRIMARY KEY,
                        section TEXT NOT NULL,
                        message_id TEXT NOT NULL)''')

    async def scoreboard_exists(self, section):
        """True if scoreboard message exists, false otherwise"""
        sec = section.lower()
        self.c.execute('''SELECT message_id FROM scoreboard_messages WHERE section = ?''', [sec])
        return self.c.fetchone() is not None

    async def populate_scoreboard(self, section):
        """Fill the scoreboard with teams and points."""
        sec = section.lower()

        self.c.execute('''SELECT id, name, score 
                        FROM scoreboard_teams 
                        WHERE section = ?
                        ORDER BY score DESC''', [sec])
        values = self.c.fetchall()

        e = discord.Embed(title="Programming Competition Scoreboard ({})".format(sec.capitalize()),
                          color=discord.Color(16712762),
                          timestamp=datetime.datetime.now(tz=self.tz))
        e.set_footer(text="Updated")

        for v in values:
            self.c.execute('''SELECT member_id FROM scoreboard_members WHERE belongs_to = ?''', [v[0]])
            member_ids = self.c.fetchall()
            member_list = ""
            for member_id in member_ids:
                member_list += "<@{}> ".format(member_id[0])
            e.add_field(name="{}: {}".format(v[1], v[2]), value=member_list, inline=False)

        chan = await self.bot.fetch_channel(self.sections[sec])
        if await self.scoreboard_exists(sec):
            self.c.execute('''SELECT message_id FROM scoreboard_messages WHERE section = ?''', [sec])
            message_id = int(self.c.fetchone()[0])

            msg = await chan.fetch_message(message_id)

            await msg.edit(embed=e)
        else:
            msg = await chan.send(embed=e)
            self.c.execute('''INSERT INTO scoreboard_messages
                                (section, message_id)
                                VALUES(?, ?)''', (sec, str(msg.id)))

            self.conn.commit()

    @commands.command(name="team")
    @commands.check(is_manager)
    async def _team(self, ctx, team_name="", section=""):
        """Add a collection of members to a team.

        [section] is not required if the team already exists. However, if the team does not exist, a section must be
        specified so it can be created."""
        if team_name == "":
            await ctx.send("Please specify a team name with this command. For help, type `!!help`.")
            return

        # Determine if team exists
        team_exists = False
        self.c.execute('''SELECT ID FROM scoreboard_teams WHERE name = ?''', [team_name])
        team_id = self.c.fetchone()
        if team_id is not None:
            team_exists = True

        if not team_exists:
            if section.lower() not in self.sections:
                await ctx.send("Please specify a section with this command. Valid values are `blue` or `silver`. For "
                               "help, type `!!help`.")
                return

            self.c.execute('''INSERT INTO scoreboard_teams 
                            (name, section)
                            VALUES(?, ?)''', (team_name, section.lower()))

            self.conn.commit()

            # Fetch ID of new team
            self.c.execute('''SELECT ID FROM scoreboard_teams WHERE name = ?''', [team_name])
            team_id = self.c.fetchone()

        team_id = team_id[0]

        for mention in ctx.message.mentions:
            member_id = str(mention.id)
            self.c.execute('''INSERT INTO scoreboard_members
                            (member_id, belongs_to)
                            VALUES(?, ?)''', (member_id, team_id))

        self.conn.commit()

        await self.populate_scoreboard(section.lower())

        await ctx.message.add_reaction("✅")

    @_team.error
    async def _team_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise err

    @commands.command(name="points", aliases=["point", "score"])
    @commands.check(is_manager)
    async def _points(self, ctx, team_name="", points=""):
        """Modify a team's point value, then update the scoreboard."""
        if team_name == "":
            await ctx.message.add_reaction("❌")
            await ctx.send("Please specify a team name with this command. For help, type `!!help`.")
            return

        # Determine if team exists
        team_exists = False
        self.c.execute('''SELECT id, score, section FROM scoreboard_teams WHERE name = ?''', [team_name])
        team = self.c.fetchone()
        if team is not None:
            team_exists = True

        if not team_exists:
            await ctx.message.add_reaction("❌")
            await ctx.send("Unknown team. For help, type `!!help`.")
            return

        try:
            point_delta = int(points)
        except ValueError:
            await ctx.message.add_reaction("❌")
            await ctx.send("Please specify an integer representing points. For help, type `!!help`.")
            return

        new_points = team[1] + point_delta

        self.c.execute('''UPDATE scoreboard_teams
                        SET score=?
                        WHERE id=?''', (new_points, team[0]))

        self.conn.commit()

        await self.populate_scoreboard(team[2])

        await ctx.message.add_reaction("✅")

    @_points.error
    async def _points_error(self, ctx, err):
        if isinstance(err, commands.CheckFailure):
            await ctx.message.add_reaction("❌")
        else:
            raise err
