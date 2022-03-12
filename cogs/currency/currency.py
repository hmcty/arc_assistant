""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Enables on-server currency.
"""

import typing
import disnake
from disnake.ext import commands

from helpers.db_manager import MemberModel, CurrencyModel
from exceptions import InternalSQLError

THANKS_AMT = 5.0
TXN_FEE = 0.5

class Currency(commands.Cog, name="currency"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="thanks", aliases=["thank", "thx"], usage="thanks <member>")
    async def thanks(self, ctx: commands.Context, member: disnake.Member):
        """
        Mints and sends ARC coins to another member (contains txn fee).
        """

        if member.id == ctx.message.author.id:
            await ctx.reply("Stop trying to print ARC coins")
            return

        sender = ctx.author.id
        sender_balance = CurrencyModel.get_balance_or_create(sender)

        receiver = member.id
        receiver_balance = CurrencyModel.get_balance_or_create(receiver)
        if sender_balance is None or receiver_balance is None:
            raise InternalSQLError()

        if sender_balance < TXN_FEE:
            await ctx.reply(f"Insufficient balance, you have {sender_balance} ARC coins. " \
                f"To send coins, you need at least {TXN_FEE} ARC coins per coin sent.")
            return

        CurrencyModel.update_balance(receiver, receiver_balance + THANKS_AMT)
        CurrencyModel.update_balance(sender, sender_balance - TXN_FEE)
        refid = "<@" + str(receiver) + ">"
        await ctx.reply(f"Gifted +{THANKS_AMT} ARC Coins to {refid}")

    @commands.command(name="pay", aliases=["send"], usage="pay <member> <amount>")
    async def pay(self, ctx: commands.Context, member: disnake.Member, amt: float):
        """
        Sends ARC coins to another member using your balance (no txn fee).
        """

        if member.id == ctx.message.author.id:
            await ctx.reply("Stop trying to print ARC coins")
            return

        if amt <= 0:
            await ctx.reply("No stealing")
            return

        sender = ctx.author.id
        sender_balance = CurrencyModel.get_balance_or_create(sender)

        receiver = member.id
        receiver_balance = CurrencyModel.get_balance_or_create(receiver)
        if sender_balance is None or receiver_balance is None:
            raise InternalSQLError()

        if sender_balance < amt:
            await ctx.reply(f"Insufficient balance, you have {sender_balance} ARC coins. " \
                f"To send coins, you need at least {TXN_FEE} ARC coins per coin sent.")
            return

        CurrencyModel.update_balance(receiver, receiver_balance + amt)
        CurrencyModel.update_balance(sender, sender_balance - amt)
        refid = "<@" + str(receiver) + ">"
        await ctx.reply(f"Paid +{amt} ARC Coins to {refid}")

    @commands.command(name="balance", usage="balance <member (Optional)>")
    async def balance(self, ctx: commands.Context,
        member: typing.Optional[disnake.Member] = None):
        """
        Prints current balance of ARC coins.
        """

        if member is None:
            member_id = ctx.author.id
            balance = CurrencyModel.get_balance_or_create(ctx.author.id)
        else:
            member_id = member.id
            balance = CurrencyModel.get_balance_or_create(member.id)

        if member is None:
            await ctx.reply(f"You have {balance} ARC coins")
        else:
            await ctx.reply(f"<@{member_id}> has {balance} ARC coins")

    @commands.command(name="leaderboard", usage="leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        """
        Prints top 15 members with most amount of ARC coins in a server.
        """

        if ctx.guild is None:
            raise commands.NoPrivateMessage(message="Command must be used in a server")

        accounts = MemberModel.get_richest(ctx.guild.id, n=15)
        if len(accounts) == 0:
            leaderboard = "Everybody is broke"
        else:
            leaderboard = f"**{ctx.guild.name}'s ARC Coin Leaderboard**\n"
            pos = 1
            for account in accounts:
                member = ctx.guild.get_member(account.member_id)
                if member is not None:
                    if member.nick is not None:
                        name = member.nick
                    else:
                        name = member.name

                    balance = CurrencyModel.get_balance_or_create(account.member_id)
                    if balance == 1:
                        leaderboard += f"{pos}: {name} with 1 coin\n"
                    else:
                        leaderboard += f"{pos}: {name} with {balance} coins\n"
                pos += 1
        await ctx.send(leaderboard)

def setup(bot):
    bot.add_cog(Currency(bot))
