""""
Modified by Harrison McCarty - Autonomous Robotics Club of Purdue
Copyright © Krypton 2021 - https://github.com/kkrypt0nn

Description:
Posts information about active commands.
"""

import json
import os
import sys

import disnake
from disnake.ext import commands
from disnake.ext.commands import Context

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx: Context):
        """
        List all commands from every Cog the bot has loaded.
        """
        prefix = config["bot_prefix"]
        if not isinstance(prefix, str):
            prefix = prefix[0]
        embed = disnake.Embed(
            title="Help", description="List of available commands:", color=0x42F56C
        )
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            command_list = [command.name for command in commands]
            command_usage = [command.signature for command in commands ]
            command_description = [command.help for command in commands]
            help_text = "\n".join(
                f"{prefix}{n} {u} \n ```{h}```" for n, u, h
                    in zip(command_list, command_usage, command_description)
            )
            embed.add_field(
                name=i.capitalize(), value=f"{help_text}", inline=False
            )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
