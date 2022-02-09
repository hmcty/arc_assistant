""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Enables on-server currency.
"""

import json
import os
import sys
import sqlite3

import discord
from discord.ext import commands

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Currency(commands.Cog, name="currency"):
    def __init__(self, bot):
        self.bot = bot
        with self.open_db() as c:
            c.execute("CREATE TABLE IF NOT EXISTS currency(member INT, balance INT)")

    def open_db(self):
        return sqlite3.connect(config["db"], timeout=10)

    @commands.command(name="thanks", aliases=["pay"])
    async def thanks(self, ctx: commands.Context, member: discord.Member):
        """
        Grants member a single ARC coin.
        """

        if member.id == ctx.message.author.id:
            refid = "<@" + str(ctx.message.author.id) + ">"
            await ctx.send(refid + " stop trying to print ARC coins.")
            return

        try:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM currency WHERE member=(?)", (member.id,)
                ).fetchone()
                if result is None:
                    c.execute("INSERT INTO currency VALUES (?, ?)", (member.id, 1))
                else:
                    c.execute(
                        "UPDATE currency SET balance=(?) WHERE member=(?)",
                        (result[1] + 1, result[0]),
                    )

                refid = "<@" + str(member.id) + ">"
                await ctx.send("Gave +1 ARC Coins to {}".format(refid))
        except sqlite3.Error as e:
            await ctx.send("Unable to produce coin: {}".format(e.args[0]))

    @commands.command(name="balance")
    async def balance(self, ctx: commands.Context):
        """
        Prints current balance of ARC coins.
        """
        name = ctx.message.author.name
        id = ctx.message.author.id

        with self.open_db() as c:
            result = c.execute(
                "SELECT * FROM currency WHERE member=(?)", (id,)
            ).fetchone()

            if result is None:
                balance = 0
            else:
                balance = result[1]

            await ctx.send("Current balance for {}: {}".format(name, balance))

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        """
        Prints top 5 members with most amount of ARC coins.
        """

        with self.open_db() as c:
            results = c.execute(
                "SELECT * FROM currency ORDER BY balance desc LIMIT 5"
            ).fetchall()

        if len(results) == 0:
            leaderboard = "Everybody is broke"
        elif ctx.guild is not None:
            leaderboard = "**ARC Coin Leaderboard**\n"
            pos = 1
            for result in results:
                member = ctx.guild.get_member(result[0])
                if member is not None:
                    if member.nick is not None:
                        name = member.nick
                    else:
                        name = member.name

                    if result[1] == 1:
                        leaderboard += "{}: {} with {} coin\n".format(
                            pos, name, result[1]
                        )
                    else:
                        leaderboard += "{}: {} with {} coins\n".format(
                            pos, name, result[1]
                        )
                pos += 1
        else:
            leaderboard = "Command can only be used in a guild."
        await ctx.send(leaderboard)

    @commands.command(name="set")
    async def set(self, ctx: commands.Context, member: discord.Member, amount: int):
        """
        Deletes cached verification information (OWNER-ONLY COMMAND).
        """

        if member is None:
            refid = "<@" + str(ctx.message.author.id) + ">"
            await ctx.send(refid + " you didn't say who you're sending money too.")
        elif ctx.message.author.id in config["owners"]:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM currency WHERE member=(?)", (member.id,)
                ).fetchone()
                if result is None:
                    c.execute("INSERT INTO currency VALUES (?, ?)", (member.id, amount))
                else:
                    c.execute(
                        "UPDATE currency SET balance=(?) WHERE member=(?)",
                        (amount, member.id),
                    )

            await ctx.send(
                "{} set {} balance to {}".format(
                    "<@" + str(ctx.message.author.id) + ">",
                    "<@" + str(member.id) + ">",
                    amount,
                )
            )
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B,
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Currency(bot))
