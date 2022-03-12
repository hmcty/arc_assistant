""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Enables server bounties.
"""

import disnake
from disnake.ext import commands

from helpers.db_manager import CurrencyModel, BountyModel
from exceptions import InternalSQLError

class Bounty(commands.Cog, name="bounty"):
    def __init__(self, bot):
        self.bot = bot
        self.claims = {}

    @commands.command(name="bounty", usage="bounty <title> <PR url> <amount>")
    async def bounty(self, ctx: commands.Context, title: str, url: str, amt: float):
        """
        Open bounty for someone to review a PR or resolve an issue.
        """

        sender = ctx.author.id
        sender_balance = CurrencyModel.get_balance_or_create(sender)
        if sender_balance is None:
            raise InternalSQLError()

        if sender_balance < amt:
            await ctx.reply(f"Insufficient balance, you have {sender_balance} ARC coins.")
            return

        bounty = BountyModel.get(title)
        if bounty:
            await ctx.reply("A bounty with that title already exists.")
            return

        embed = disnake.Embed(title=f"Bounty: {title}",
            description=f"Reward amount: {amt} \n " \
                f"Click URL above and use `.claim {title}`",
            url=url, color=0x00ff00)
        bounty_msg = await ctx.channel.send(embed=embed)

        BountyModel.create(title, sender, ctx.guild.id, ctx.channel.id, bounty_msg.id, amt)
        CurrencyModel.update_balance(sender, sender_balance - amt)

    @commands.command(name="claim", usage="claim <title>")
    async def claim(self, ctx: commands.Context, title: str):
        """
        Claim a bounty.
        """

        bounty = BountyModel.get(title)
        if bounty is None:
            await ctx.reply("No bounty with that title exists.")
            return

        claim_msg = await ctx.channel.send(
            f"{ctx.author.mention} claimed {bounty.title}, <@{bounty.owner_id}> react to accept."
        )
        self.claims[claim_msg.id] = (ctx.author.id, bounty.title)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent):
        if payload.member is None or payload.member.bot:
            return

        if payload.message_id in self.claims:
            receiver_id, title = self.claims[payload.message_id]
            bounty = BountyModel.get(title)
            if payload.user_id == bounty.owner_id:
                balance = CurrencyModel.get_balance_or_create(receiver_id)
                CurrencyModel.update_balance(receiver_id, balance + bounty.amt)

                channel = self.bot.get_channel(bounty.channel_id)
                bounty_msg = await channel.fetch_message(bounty.message_id)
                embed = disnake.Embed(title=f"Bounty: {bounty.title}",
                    description=f"Bounty claimed by <@{receiver_id}>")
                await bounty_msg.edit(embed=embed)

                bounty.complete()
                del self.claims[payload.message_id]
                await channel.send(f"Bounty '{bounty.title}' claimed by <@{receiver_id}>.")

def setup(bot):
    bot.add_cog(Bounty(bot))
