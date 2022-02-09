""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Sends updates from linked calendar.
"""

import json
import os
import sys
from datetime import datetime

import discord
from discord.ext import commands, tasks

from helpers import calendar_util as util

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Calendar(commands.Cog, name="calendar"):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminder.start()

    async def send_update(self, ctx: commands.Context, calendar_events, span_msg):
        if not calendar_events:
            await ctx.send(content="No calendar events {}.".format(span_msg))
        else:
            embed = discord.Embed(title=span_msg + "'s events:")

            description = util.construct_calendar_msg(calendar_events[0])
            for i in range(1, len(calendar_events)):
                description += "\n\n"
                description += util.construct_calendar_msg(calendar_events[i])

            embed.description = description
            await ctx.send(embed=embed)

    @tasks.loop(hours=1)
    async def check_reminder(self):
        now = datetime.utcnow()

        # 12am EST in UTC
        if now.hour == 13:
            if now.weekday() == 0:
                await self.send_weekly_reminder()
            else:
                await self.send_daily_reminder()

    async def send_daily_reminder(self):
        guild = self.bot.get_guild(config["server_id"])
        if guild is not None:
            for id in config["reminder_channels"]:
                channel = guild.get_channel(id)
                if channel is not None:
                    await self.get_todays_events(channel)

    async def send_weekly_reminder(self):
        guild = self.bot.get_guild(config["server_id"])
        if guild is not None:
            for id in config["reminder_channels"]:
                channel = guild.get_channel(id)
                if channel is not None:
                    await self.get_weeks_events(channel)

    @commands.command(name="today")
    async def get_todays_events(self, ctx: commands.Context):
        """
        Prints a list of scheduled events for the current day.
        """
        await self.send_update(
            ctx, util.collect_today(config["google_calendar_id"]), "today"
        )

    @commands.command(name="week")
    async def get_weeks_events(self, ctx):
        """
        Prints a list of scheduled events for the current week.
        """
        await self.send_update(
            ctx, util.collect_week(config["google_calendar_id"]), "this week"
        )


def setup(bot):
    bot.add_cog(Calendar(bot))
