""""
Modified by Harrison McCarty - Autonomous Robotics Club of Purdue
Copyright © Krypton 2021 - https://github.com/kkrypt0nn

Description:
Holds common utility commands.
"""

import json
import os
import random
import sys
import sqlite3

import discord
from discord.ext import commands

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

con = sqlite3.connect(config["db"])
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS rolemenu(menu INT, role TEXT, emoji TEXT)')
con.commit()

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
                   'Signs point to yes.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        
        refid = "<@" + str(context.message.author.id) + "> "
        await context.send(
            refid + answers[random.randint(0, len(answers) - 1)]
        )

    @commands.command(name="create_role_menu")
    async def create_role_menu(self, context, title, *, message):
        """
        Allow users to set roles through reaction.

        Seperate each role by comma (',) and each emoji/role pair by pipe ('|').
        Watch for additional spaces, may corrupt input.
        """
        menu_desc = "React to give yourself a role. \n\n"
        roles = []
        emojis = []
        info = message.strip().split(",")
        for entry in info:
            entry = entry.split("|")
            if len(entry) != 2:
                user_ref = "<@" + str(context.author.id) + ">"
                await context.send(
                    user_ref + " each role needs a respective emoji."
                )
                return
            role = entry[0].strip()
            emoji = entry[1].strip()
            menu_desc += "{}: `{}`\n".format(emoji, role)
            roles.append(role)
            emojis.append(emoji)

        embed = discord.Embed(
            title=title,
            description=menu_desc,
            color=0x42F56C
        )
        menu = await context.send(embed=embed)

        guild = self.bot.get_guild(config["server_id"])
        for emoji, role_name in zip(emojis, roles):
            role = discord.utils.get(guild.roles, name=role_name)
            if role is None:
                user_ref = "<@" + str(context.author.id) + ">"
                await context.send(
                    user_ref + " role: '{}' doesn't exist.".format(role_name)
                )
                continue

            cur.execute("INSERT INTO rolemenu VALUES (?, ?, ?)",
            (menu.id, role_name, emoji))
            await menu.add_reaction(emoji)
        con.commit()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member is None or payload.member.bot:
            return

        results = cur.execute(
            "SELECT * FROM rolemenu WHERE menu=(?)",
            (payload.message_id,)
        ).fetchall()
        if len(results) > 0:
            guild = self.bot.get_guild(config["server_id"])
            for result in results:
                if result[2] == str(payload.emoji):
                    role = discord.utils.get(guild.roles, name=result[1])
                    if role not in payload.member.roles:
                        await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        results = cur.execute(
            "SELECT * FROM rolemenu WHERE menu=(?)",
            (payload.message_id,)
        ).fetchall()
        if len(results) > 0:
            guild = self.bot.get_guild(config["server_id"])
            member = guild.get_member(payload.user_id)
            if member is None:
                return
            for result in results:
                if result[2] == str(payload.emoji):
                    role = discord.utils.get(guild.roles, name=result[1])
                    if role in member.roles:
                        await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        cur.execute(
            "DELETE FROM rolemenu WHERE menu=(?)",
            (payload.message_id,)
        )

def setup(bot):
    bot.add_cog(General(bot))
