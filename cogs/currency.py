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

    def open_db(self):
        con = sqlite3.connect(config["db"])
        cur = con.cursor()
        cur.execute(
          'CREATE TABLE IF NOT EXISTS currency(member INT, balance INT)'
        )
        con.commit()
        return con, cur

    @commands.command(name="thanks", aliases=['pay'])
    async def thanks(self, context, member: discord.Member):
        """
        Grants member a single ARC coin.
        """
        con, cur = self.open_db()

        if member.id == context.message.author.id:
            refid = "<@" + str(context.message.author.id) + ">"
            await context.send(
                refid + " stop trying to print ARC coins."
            )
            return

        try:
            result = cur.execute(
                "SELECT * FROM currency WHERE member=(?)", (member.id,)
            ).fetchone()
            if result is None:
                cur.execute(
                    "INSERT INTO currency VALUES (?, ?)", (member.id, 1)
                )
            else:
                cur.execute(
                    "UPDATE currency SET balance=(?) WHERE member=(?)",
                    (result[1] + 1, result[0])
                )
            con.commit()
            con.close()

            refid = "<@" + str(member.id) + ">"
            await context.send("Gave +1 ARC Coins to {}".format(refid))
        except sqlite3.Error as e:
            await context.send("Unable to produce coin: {}".format(e.args[0]))

    @commands.command(name="balance")
    async def balance(self, context):
        """
        Prints current balance of ARC coins.
        """
        con, cur = self.open_db()
        name = context.message.author.name
        id = context.message.author.id

        result = cur.execute(
            "SELECT * FROM currency WHERE member=(?)", (id,)).fetchone()
        if result is None:
            balance = 0
        else:
            balance = result[1]
        con.close()

        await context.send("Current balance for {}: {}".format(name, balance))

    @commands.command(name="leaderboard")
    async def leaderboard(self, context):
        """
        Prints top 5 members with most amount of ARC coins.
        """
        con, cur = self.open_db()
        results = cur.execute(
            "SELECT * FROM currency ORDER BY balance desc LIMIT 5").fetchall()
        con.close()
        if len(results) == 0:
            leaderboard = "Everybody is broke"
        elif context.guild is not None:
            leaderboard = "**ARC Coin Leaderboard**\n"
            pos = 1
            for result in results:
                member = context.guild.get_member(result[0])
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
        await context.send(leaderboard)

    @commands.command(name="set")
    async def set(self, context, member: discord.Member, amount: int):
        """
        Deletes cached verification information (OWNER-ONLY COMMAND).
        """
        con, cur = self.open_db()
        if member is None:
            refid = "<@" + str(context.message.author.id) + ">"
            await context.send(
                refid + " you didn't say who you're sending money too."
            )
        elif context.message.author.id in config["owners"]:
            result = cur.execute(
                "SELECT * FROM currency WHERE member=(?)", (member.id,)
            ).fetchone()
            if result is None:
                cur.execute(
                    "INSERT INTO currency VALUES (?, ?)", (member.id, amount)
                )
            else:
                cur.execute(
                    "UPDATE currency SET balance=(?) WHERE member=(?)",
                    (amount, member.id)
                )
            con.commit()
            
            await context.send(
                "{} set {} balance to {}".format(
                    "<@" + str(context.message.author.id) + ">",
                    "<@" + str(member.id) + ">",
                    amount)
            )
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        
        con.close()

def setup(bot):
    bot.add_cog(Currency(bot))
