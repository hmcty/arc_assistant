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

con = sqlite3.connect(config["db"])
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS verification(
    member INT,
    code INT,
    verified INT);
""")
con.commit()


class Verification(commands.Cog, name="verification"):
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, message):
        """
        Called when a direct message is received.
        """

        message_content = message.content.strip()
        if len(message_content) == 6 and message_content.isdigit():
            # Handle user DMing code
            id = message.author.id
            code = int(message_content)
            result = cur.execute(
                "SELECT code FROM verification WHERE member=(?)",
                (id,)).fetchone()

            if result is None:
                await message.channel.send(
                    "I wasn't ready for a code, try sending your email again.")
            elif result[0] == code:
                guild = self.bot.get_guild(config["server_id"])
                role = discord.utils.get(guild.roles, name=ROLE_NAME)
                member = discord.utils.get(
                    guild.members, name=message.author.name)
                if role not in member.roles:
                    await member.add_roles(role)
                await message.channel.send(
                    "You are verified on {}.".format(guild.name))
            else:
                await message.channel.send("Invalid code.")
        elif email.check(message_content):
            # Handle user DMing valid email
            if message_content.split("@")[1] == DOMAIN_NAME:
                code = random.randint(100000, 999999)
                id = message.author.id
                result = cur.execute(
                    "SELECT * FROM verification WHERE member=(?)", (id,)
                ).fetchone()
                if result is None:
                    cur.execute(
                        "INSERT INTO verification VALUES (?, ?, ?)",
                        (id, code, 0))
                else:
                    cur.execute(
                        """
                        UPDATE verification SET code=(?), verified=(?)
                        WHERE member=(?);
                        """,
                        (code, 0, id))
                con.commit()

                emailmessage = Mail(
                    from_email=config['sendgrid_email'],
                    to_emails=message_content,
                    subject='Verify your server email',
                    html_content=str(code))

                try:
                    success_msg = "Email sent. " + \
                        "**Reply here with your verification code**. " + \
                        "If you haven't received it, check your spam folder."
                    sg = SendGridAPIClient(config['sendgrid_api_key'])
                    sg.send(emailmessage)
                    await message.channel.send(success_msg)
                except Exception as e:
                    await message.channel.send("Email failed to send.")
            else:
                await message.channel.send("You need to use a Purdue email.")
        else:
            # Handle user DMing something other than a valid email or code
            await message.channel.send(
                "There's an error in your message. Re-evaluate and resend.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        DMs user to verify email address is under Purdue domain.
        """
        id = member.id
        result = cur.execute(
            "SELECT * FROM verification WHERE member=(?)", (id,)).fetchone()

        if result is not None and result[2] == 1:
            refid = "<@" + str(id) + ">"
            await member.send(refid + " you've already been verified.")
        else:
            await member.send(
                "Reply here with your @{} email address.".format(DOMAIN_NAME)
            )

    @commands.command(name="verify")
    async def verify(self, context):
        """
        DMs user to verify email address is under Purdue domain.
        """
        id = context.message.author.id
        result = cur.execute(
            "SELECT * FROM verification WHERE member=(?)", (id,)).fetchone()

        if result is not None and result[2] == 1:
            refid = "<@" + str(id) + ">"
            await context.send(refid + " you've already been verified.")
        else:
            await context.message.author.send(
                "Reply here with your @{} email address.".format(DOMAIN_NAME)
            )


def setup(bot):
    bot.add_cog(Verification(bot))
