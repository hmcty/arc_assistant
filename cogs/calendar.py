""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Sends updates from linked calendar.
"""

import json
import os
import sys

import discord
from discord.ext import commands

from helpers import calendar_util

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Calendar(commands.Cog, name="calendar"):
    def __init__(self, bot):
        self.bot = bot

    async def send_update(self, context, calendar_events, span_msg):
        if not calendar_events:
            await context.send(
                content="No calendar events {}.".format(span_msg)
            )
        else:
            await context.send(span_msg + "'s events:")
            for calendar_event in calendar_events:
                await context.send(
                    embed=calendar_util.construct_calendar_msg(calendar_event)
                )

    @commands.command(name="get_todays_events")
    async def get_todays_events(self, context):
        """
        Prints a list of scheduled events for the current day.
        """
        await self.send_update(context,
                               calendar_util.collect_today(
                                   config["google_calendar_id"]),
                               "today")

    @commands.command(name="get_weeks_events")
    async def get_weeks_events(self, context):
        """
        Prints a list of scheduled events for the current week.
        """
        await self.send_update(context,
                               calendar_util.collect_week(
                                   config["google_calendar_id"]),
                               "this week")


def setup(bot):
    bot.add_cog(Calendar(bot))
