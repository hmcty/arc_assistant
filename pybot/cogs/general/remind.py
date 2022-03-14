""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Create and post small reminders.
"""

import datetime as dt
import dateparser as dp
from typing import List

import disnake
from disnake.ext import commands, tasks

class RemindFlags(commands.FlagConverter):
    reason: str = ""
    time: str

class Reminder(object):
    def __init__(self, ctx: commands.Context, members: commands.Greedy[disnake.Member],
        reason: str, time: dt.datetime):
        self.ctx = ctx
        self.members = members
        self.time = time
        self.reason = reason
    
    async def send_msg(self):
        refids = ", ".join(f"<@{x.id}>" for x in self.members)
        if self.reason == "":
            await self.ctx.send(f"{refids} Here's your reminder")
        else:
            await self.ctx.send(f"{refids} {self.reason}")

    def is_ready(self):
        return self.time < dt.datetime.now()

class Remind(commands.Cog, name="remind"):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []

    @tasks.loop(seconds=10)
    async def send_reminders(self):
        for reminder in self.reminders:
            if reminder.is_ready():
                self.reminders.remove(reminder)
                await reminder.send_msg()

        if len(self.reminders) == 0:
            self.send_reminders.stop()

    @commands.command(name="remind", 
        usage="remind <member1> <member2> ... reason: <reason (optional)> time: <time info>")
    async def add_remind(self, ctx: commands.Context, members: commands.Greedy[disnake.Member],
        *, flags: RemindFlags):
        """
        Reminds the list of members of a custom message at a set time.
        'time info' follows example format: "Jan 02 01:30 AM"
        """

        rtime = dp.parse(flags.time)
        self.reminders.append(Reminder(ctx, members, flags.reason, rtime))
        await ctx.send(f"Reminder set for {rtime.strftime('%b %d %I:%M %p')}")
        if not self.send_reminders.is_running():
            self.send_reminders.start()

def setup(bot):
    bot.add_cog(Remind(bot))
