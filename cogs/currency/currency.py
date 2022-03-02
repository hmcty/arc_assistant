""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Enables on-server currency.
"""

import json
import os
import sys
import sqlite3
import typing
from datetime import date

import disnake
from disnake.ext import commands

from helpers import arcdle
from helpers.db_manager import MemberModel

from exceptions import InternalSQLError

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Currency(commands.Cog, name="currency"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="thanks", aliases=["pay"])
    async def thanks(self, ctx: commands.Context, member: disnake.Member):
        """
        Grants member a single ARC coin.
        """

        if member.id == ctx.message.author.id:
            await ctx.reply("Stop trying to print ARC coins")
            return
        
        if ctx.guild is None:
            raise commands.NoPrivateMessage(message="Command must be used in a server")

        sender = MemberModel.get_or_create(ctx.author.id, ctx.guild.id)
        receiver = MemberModel.get_or_create(member.id, ctx.guild.id)
        if sender is None or receiver is None:
            raise InternalSQLError()

        if sender.balance < 1:
            await ctx.reply(f"Insufficient balance, you have {sender.balance} ARC coins")
            return

        receiver.update_balance(receiver.balance + 1)
        sender.update_balance(sender.balance - 1)
        refid = "<@" + str(member.id) + ">"
        await ctx.reply("Gave +1 ARC Coins to {}".format(refid))

    @commands.command(name="balance")
    async def balance(self, ctx: commands.Context,
        member: typing.Optional[disnake.Member] = None):
        """
        Prints current balance of ARC coins.
        """
        
        if ctx.guild is None:
            raise commands.NoPrivateMessage(message="Command must be used in a server")

        if member is None:
            account = MemberModel.get_or_create(ctx.author.id, ctx.guild.id)
        else:
            account = MemberModel.get_or_create(member.id, ctx.guild.id)
        if account is None:
            raise InternalSQLError()

        if member is None:
            await ctx.reply(f"You have {account.balance} ARC coins")
        else:
            await ctx.reply(f"<@{account.member_id}> has {account.balance} ARC coins")

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        """
        Prints top 5 members with most amount of ARC coins.
        """

        accounts = MemberModel.get_richest(n=5)
        if len(accounts) == 0:
            leaderboard = "Everybody is broke"
        elif ctx.guild is not None:
            leaderboard = "**ARC Coin Leaderboard**\n"
            pos = 1
            for account in accounts:
                member = ctx.guild.get_member(account.member_id)
                if member is not None:
                    if member.nick is not None:
                        name = member.nick
                    else:
                        name = member.name

                    if account.balance == 1:
                        leaderboard += f"{pos}: {name} with 1 coin\n"
                    else:
                        leaderboard += f"{pos}: {name} with {account.balance} coins\n"
                pos += 1
        else:
            raise commands.NoPrivateMessage(message="Command must be used in a server")
        await ctx.send(leaderboard)

    @commands.command(name="set")
    async def set(self, ctx: commands.Context, member: disnake.Member, amount: int):
        """
        Deletes cached verification information.
        """

        if ctx.guild is None:
            raise commands.NoPrivateMessage(message="Command must be used in a server")

        if ctx.message.author.id in config["owners"]:
            account = MemberModel.get_or_create(member.id, ctx.guild.id)
            if account is None:
                raise InternalSQLError()
            
            account.update_balance(amount)

            await ctx.reply(
                "Set {} balance to {}".format(
                    "<@" + str(member.id) + ">",
                    amount,
                )
            )
        else:
            raise commands.MissingPermissions([])

def setup(bot):
    bot.add_cog(Currency(bot))
