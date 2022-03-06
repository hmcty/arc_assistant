""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Verifies email domain of new members.
"""

import json
import os
import sys
import random
import smtplib
from email.message import EmailMessage

import disnake
from disnake.ext import commands

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from helpers import email
from helpers.db_manager import VerificationModel, MemberModel

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

def send_verif_email(to: str, code: int):
    email_msg = EmailMessage()
    email_msg.set_content("Your code is: {}".format(code))
    email_msg["Subject"] = "Purdue ARC Verification Code"
    email_msg["From"] = config["smtp_user"]
    email_msg["To"] = to

    s = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
    s.ehlo()
    s.starttls()
    s.login(config["smtp_user"].split("@")[0], config["smtp_password"])

    s.send_message(email_msg)
    s.quit()

class Verification(commands.Cog, name="verification"):
    def __init__(self, bot):
        self.bot = bot

    async def handle_message(self, msg: disnake.Message):
        """
        Called when a direct message is received for verification.
        """

        msg_content = msg.content.strip()

        member_verif = None
        verif_config = None
        for i in MemberModel.get_all(msg.author.id):
            verif_config = VerificationModel.get(i.guild_id)
            if verif_config is None or i.verified == 1:
                continue
            member_verif = i
            break

        if member_verif is None:
            return        

        if msg_content.isdigit() and int(msg_content) == member_verif.code:
            # TODO: Handle bizarre circumstance where don't exist
            guild = self.bot.get_guild(member_verif.guild_id)
            role = guild.get_role(verif_config.role_id)
            member = guild.get_member(msg.author.id)
            if role not in member.roles:
                await member.add_roles(role)
            member_verif.update_verified(1)
            await msg.channel.send("You are verified on {}.".format(guild.name))
        elif member_verif.code != 0:
            await msg.channel.send("Invalid code, please try again")
        elif email.check(msg_content):
            # Handle user DMing valid email
            if msg_content.split("@")[1] == verif_config.domain:
                code = random.randint(100000, 999999)
                member_verif.update_code(code)

                try:
                    send_verif_email(msg_content, code)
                    await msg.channel.send("Email sent. " \
                        "**Reply here with your verification code**. " \
                        "If you haven't received it, check your spam folder.")
                except Exception as e:
                    # TODO: Update to actually handle exception
                    await msg.channel.send("Email failed to send.")
            else:
                await msg.channel.send("You need to use a Purdue email.")
        else:
            await msg.channel.send("Invalid email, please try again")

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        """
        DMs user to verify email address is under Purdue domain.
        """

        MemberModel.get_or_create(member.id, member.guild.id)
        config = VerificationModel.get(member.guild.id)
        if config is not None:
            await member.send(
                f"Reply here with your @{config.domain} email address " \
                f"to be verified on the {member.guild.name}"
            )

    @commands.command(name="configureverify")
    async def configure(self, ctx: commands.Context, role: disnake.Role,
        domain: str):
        
        if ctx.guild is None:
            raise commands.NoPrivateMessage(message="Command must be used in a server")

        VerificationModel.configure(ctx.guild.id, role.id, domain)
        await ctx.reply(f"Verification configured for @{domain} domains")

    @commands.command(name="verify")
    async def verify(self, ctx: commands.Context):
        """
        DMs member to verify email address is under Purdue domain.
        """

        if ctx.guild is None:
            raise commands.NoPrivateMessage(message="Command must be used in a server")
        
        config = VerificationModel.get(ctx.guild.id)
        if config is not None:
            member_verif = MemberModel.get_or_create(ctx.author.id, ctx.guild.id)
            member_verif.update_verified(0)
            member_verif.update_code(0)
            await ctx.message.author.send(
                "Reply here with your @{} email address.".format(config.domain)
            )
        else:
            await ctx.reply("You must configure verification settings, contact server admin")

def setup(bot):
    bot.add_cog(Verification(bot))
