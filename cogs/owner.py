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
    async def shutdown(self, ctx: commands.Context):
        """
        Make the bot shutdown.
        """
        if ctx.message.author.id in config["owners"]:
            await ctx.send("See ya :wave:")
            await self.bot.close()
        else:
            raise commands.MissingPermissions([])

    @commands.command(name="say", aliases=["echo"])
    async def say(self, ctx: commands.Context, *, msg: str):
        """
        Echo your message.
        """
        if ctx.message.author.id in config["owners"]:
            await ctx.send(msg)
        else:
            raise commands.MissingPermissions([])

    @commands.command(name="embed")
    async def embed(self, ctx: commands.Context, *, msg: str):
        """
        Echo your message with embed.
        """
        if ctx.message.author.id in config["owners"]:
            embed = discord.Embed(description=msg, color=0x42F56C)
            await ctx.send(embed=embed)
        else:
            raise commands.MissingPermissions([])

def setup(bot):
    bot.add_cog(Owner(bot))
