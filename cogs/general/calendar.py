""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Sends updates from linked calendar.
"""

import json
import os
import sys
from datetime import datetime

import disnake
from disnake.ext import commands, tasks

from helpers import calendar_util as util
from helpers.db_manager import CalendarModel

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

class Calendar(commands.Cog, name="calendar"):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminder.start()

    async def send_update(self, title: str, channel: disnake.TextChannel, events):
        if not events:
            await channel.send(content="No calendar events {}.".format(title))
        else:
            embed = disnake.Embed(title=f"{title}'s events:")

            event_ids = {} 
            event_ids[events[0]["id"]] = True
            description = util.construct_calendar_msg(events[0])
            for i in range(1, len(events)):
                if events[i]["id"] in event_ids:
                    continue
                description += "\n\n"
                description += util.construct_calendar_msg(events[i])
                event_ids[events[i]["id"]] = True

            embed.description = description
            await channel.send(embed=embed)

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
        calendars = CalendarModel.get_all()
        events = {}
        for calendar in calendars:
            cal_events = util.collect_today([calendar.calendar_id])
            if calendar.channel_id not in events:
                events[calendar.channel_id] = [cal_events]
            else:
                events[calendar.channel_id] += cal_events
        
        for channel_id, cal_events in events.items():
            channel = self.bot.get_channel(channel_id)
            await self.send_update("today", channel, cal_events)

    async def send_weekly_reminder(self):
        calendars = CalendarModel.get_all()
        events = {}
        for calendar in calendars:
            cal_events = util.collect_week([calendar.calendar_id])
            if calendar.channel_id not in events:
                events[calendar.channel_id] = [cal_events]
            else:
                events[calendar.channel_id] += cal_events
        
        for channel_id, cal_events in events.items():
            channel = self.bot.get_channel(channel_id)
            await self.send_update("this week", channel, cal_events)

    @commands.command(name="today")
    async def get_todays_events(self, ctx: commands.Context):
        """
        Prints a list of scheduled events for the current day.
        """
        calendars = CalendarModel.get_by_guild(ctx.guild.id)
        calendar_ids = [calendar.calendar_id for calendar in calendars]
        events = util.collect_today(calendar_ids)
        await self.send_update(
            "today", ctx.channel, events
        )

    @commands.command(name="week")
    async def get_weeks_events(self, ctx):
        """
        Prints a list of scheduled events for the current week.
        """
        calendars = CalendarModel.get_by_guild(ctx.guild.id)
        calendar_ids = [calendar.calendar_id for calendar in calendars]
        events = util.collect_week(calendar_ids)
        await self.send_update(
            "this week", ctx.channel, events
        )

    @commands.command(name="addcalendar")
    async def add_calendar(self, ctx: commands.Context, calendar_id: str):
        """
        Set a channel to print calendar reminders. 
        """
        calendar = CalendarModel.get(ctx.guild.id, ctx.channel.id, calendar_id)
        calendar_name = util.get_calendar_name(calendar_id)
        if calendar:
            await ctx.reply(f"{calendar_name} calendar already added to this channel")
        elif calendar_name:
            CalendarModel.add(ctx.guild.id, ctx.channel.id, calendar_id)
            await ctx.reply(f"{calendar_name} calendar added")
        else:
            await ctx.reply("Calendar couldn't be accessed, check permissions")

    @commands.command(name="listcalendars")
    async def list_calendars(self, ctx: commands.Context):
        """
        List all calendars for a given channel.
        """
        calendars = CalendarModel.get_by_channel(ctx.guild.id, ctx.channel.id)
        if calendars:
            calendar_names = [util.get_calendar_name(calendar.calendar_id)
                for calendar in calendars]
            embed = disnake.Embed(title="Calendars:")
            embed.description = "\n".join(calendar_names)
            await ctx.reply(embed=embed)
        else:
            await ctx.reply("No calendars added to this channel")

    @commands.command(name="removecalendar")
    async def remove_calendar(self, ctx: commands.Context, calendar_id: str):
        """
        Stop calendar reminders from being to this channel.
        """
        calendar = CalendarModel.get(ctx.guild.id, ctx.channel.id, calendar_id)
        if calendar:
            calendar.remove()
            calendar_name = util.get_calendar_name(calendar.calendar_id)
            await ctx.reply(f"{calendar_name} calendar removed")
        else:
            await ctx.reply("No calendar found with that id")

def setup(bot):
    bot.add_cog(Calendar(bot))
