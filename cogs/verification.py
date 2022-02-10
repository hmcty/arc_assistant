""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Verifies email domain of new members.
"""

import json
import os
import sys
import sqlite3
import random
import smtplib
from email.message import EmailMessage

import discord
from discord.ext import commands

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from helpers import email

DOMAIN_NAME = "purdue.edu"
ROLE_NAME = "Verified"

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)


class Verification(commands.Cog, name="verification"):
    def __init__(self, bot):
        self.bot = bot
        with self.open_db() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS verification(
                member INT,
                code INT,
                verified INT);"""
            )

    def open_db(self):
        return sqlite3.connect(config["db"], timeout=20)

    async def handle_message(self, msg: discord.Message):
        """
        Called when a direct message is received for verification.
        """

        msg_content = msg.content.strip()

        if len(msg_content) == 6 and msg_content.isdigit():
            # Handle user DMing code
            id = msg.author.id
            code = int(msg_content)

            with self.open_db() as c:
                result = c.execute(
                    "SELECT code FROM verification WHERE member=(?)", (id,)
                ).fetchone()

            if result is None:
                await msg.channel.send(
                    "I wasn't ready for a code, try sending your email again."
                )
            elif result[0] == code:
                guild = self.bot.get_guild(config["server_id"])
                role = discord.utils.get(guild.roles, name=ROLE_NAME)
                member = discord.utils.get(guild.members, name=msg.author.name)
                if role not in member.roles:
                    await member.add_roles(role)
                await msg.channel.send("You are verified on {}.".format(guild.name))
            else:
                await msg.channel.send("Invalid code.")
        elif email.check(msg_content):
            # Handle user DMing valid email
            if msg_content.split("@")[1] == DOMAIN_NAME:
                code = random.randint(100000, 999999)
                id = msg.author.id

                with self.open_db() as c:
                    result = c.execute(
                        "SELECT * FROM verification WHERE member=(?)", (id,)
                    ).fetchone()
                    if result is None:
                        c.execute(
                            "INSERT INTO verification VALUES (?, ?, ?)", (id, code, 0)
                        )
                    else:
                        c.execute(
                            """
                            UPDATE verification SET code=(?), verified=(?)
                            WHERE member=(?);
                            """,
                            (code, 0, id),
                        )

                try:
                    success_msg = (
                        "Email sent. "
                        + "**Reply here with your verification code**. "
                        + "If you haven't received it, check your spam folder."
                    )

                    email_msg = EmailMessage()
                    email_msg.set_content("Your code is: {}".format(code))
                    email_msg["Subject"] = "Purdue ARC Verification Code"
                    email_msg["From"] = config["smtp_user"]
                    email_msg["To"] = msg_content

                    s = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
                    s.ehlo()
                    s.starttls()
                    s.login(config["smtp_user"].split("@")[0], config["smtp_password"])

                    s.send_message(email_msg)
                    s.quit()
                    await msg.channel.send(success_msg)
                except Exception as e:
                    await msg.channel.send("Email failed to send.")
            else:
                await msg.channel.send("You need to use a Purdue email.")
        else:
            # Handle user DMing something other than a valid email or code
            await msg.channel.send(
                "I'm not expecting a message rn :blush:"
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        DMs user to verify email address is under Purdue domain.
        """
        id = member.id

        with self.open_db() as c:
            result = c.execute(
                "SELECT * FROM verification WHERE member=(?)", (id,)
            ).fetchone()

        if result is not None and result[2] == 1:
            refid = "<@" + str(id) + ">"
            await member.send(refid + " you've already been verified.")
        else:
            await member.send(
                "Reply here with your @{} email address.".format(DOMAIN_NAME)
            )

    @commands.command(name="verify")
    async def verify(self, ctx: commands.Context):
        """
        DMs member to verify email address is under Purdue domain.
        """
        id = ctx.message.author.id

        try:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM verification WHERE member=(?)", (id,)
                ).fetchone()
        except sqlite3.Error as e:
            await ctx.send("Unable to verify: {}".format(e.args[0]))
            return

        if result is not None and result[2] == 1:
            refid = "<@" + str(id) + ">"
            await ctx.send(refid + " you've already been verified.")
        else:
            await ctx.message.author.send(
                "Reply here with your @{} email address.".format(DOMAIN_NAME)
            )

    @commands.command(name="clear")
    async def clear(self, ctx: commands.Context):
        """
        Deletes cached verification information.
        """

        if ctx.message.author.id in config["owners"]:
            with self.open_db() as c:
                c.execute("DELETE FROM verification")

            refid = "<@" + str(ctx.message.author.id) + ">"
            await ctx.send(refid + " verification cache cleared.")
        else:
            raise commands.MissingPermissions([])

def setup(bot):
    bot.add_cog(Verification(bot))
