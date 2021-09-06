""""
Modified by Harrison McCarty - Autonomous Robotics Club of Purdue
Copyright © Krypton 2021 - https://github.com/kkrypt0nn

Description:
Holds common utility commands.
"""

import json
import os
import platform
import random
import sys

import discord
from discord.ext import commands


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def info(self, context):
        """
        Get some useful (or not) information about the bot.
        """
        await context.send("Still alive lol")

    @commands.command(name="poll")
    async def poll(self, context, *, title):
        """
        Create a poll where members can vote.
        """
        embed = discord.Embed(
            title=f"{title}",
            color=0x42F56C
        )
        embed.set_footer(
            text=f"Poll created by: {context.message.author} • React to vote!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(name="8ball")
    async def eight_ball(self, context, *, question=None):
        """
        Ask any question to the bot.
        """
        answers = ['It is certain.', 'It is decidedly so.', 'You may rely on it.', 'Without a doubt.',
                   'Yes - definitely.', 'As I see, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                   'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
                   'Cannot predict now.', 'Concentrate and ask again later.', 'Don\'t count on it.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers))]}",
            color=0x42F56C
        )
        if question:
            embed.set_footer(
                text=f"The question was: {question}"
            )
        await context.send(embed=embed)

    @commands.command(name="create_role_menu")
    async def role_menu(self, context):
        """
        Allow users to set roles through reaction.
        """
        await context.send("Not implemented yet")

def setup(bot):
    bot.add_cog(General(bot))
