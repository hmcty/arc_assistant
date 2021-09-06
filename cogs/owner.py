""""
Modified by Harrison McCarty - Autonomous Robotics Club of Purdue
Copyright © Krypton 2021 - https://github.com/kkrypt0nn

Description:
Enables moderation of bot usage.
"""

import json
import os
import sys

import discord
from discord.ext import commands

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown")
    async def shutdown(self, context):
        """
        Make the bot shutdown
        """
        if context.message.author.id in config["owners"]:
            embed = discord.Embed(
                description="Shutting down. Bye! :wave:",
                color=0x42F56C
            )
            await context.send(embed=embed)
            await self.bot.close()
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="say", aliases=["echo"])
    async def say(self, context, *, args):
        """
        The bot will say anything you want.
        """
        if context.message.author.id in config["owners"]:
            await context.send(args)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="embed")
    async def embed(self, context, *, args):
        """
        The bot will say anything you want, but within embeds.
        """
        if context.message.author.id in config["owners"]:
            embed = discord.Embed(
                description=args,
                color=0x42F56C
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))
