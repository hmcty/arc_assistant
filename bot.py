""""
Modified by Harrison McCarty - Autonomous Robotics Club of Purdue
Copyright © Krypton 2021 - https://github.com/kkrypt0nn
Description:
"""

import json
import os
import platform
import random
import sys
import logging as log

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import tasks, commands
from disnake.ext.commands import Bot
from disnake.ext.commands import Context

from helpers.db_manager import init_db, MemberModel, ARCdleModel
from sqlalchemy import create_engine
from sqlalchemy import sessionmaker

import exceptions

#
# Configuration
#

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

# Setup logging
logger = log.getLogger()
logger.setLevel(log.NOTSET)

console_handler = log.StreamHandler()
console_handler.setLevel(log.ERROR)
console_handler_format = "%(asctime)s | %(levelname)s: %(message)s"
console_handler.setFormatter(log.Formatter(console_handler_format))
logger.addHandler(console_handler)

file_handler = log.FileHandler(config["log"])
file_handler.setLevel(log.INFO)
file_handler_format = '%(asctime)s | %(levelname)s | %(lineno)d: %(message)s'
file_handler.setFormatter(log.Formatter(file_handler_format))
logger.addHandler(file_handler)

#
# Define bot commands
#

intents = disnake.Intents.default()
intents.members = True
intents.reactions = True
bot = Bot(command_prefix=config["bot_prefix"], intents=intents)

# Create session maker
engine = create_engine("sqlite+pysqlite:///:memory:")
Session = sessionmaker(engine)
bot.session = Session

# Removes the default help command
bot.remove_command("help")

def load_commands(command_type: str) -> None:
    for file in os.listdir(f"./cogs/{command_type}"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{command_type}.{extension}")
                log.info(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                log.error(f"Failed to load extension {extension}\n{exception}")

if __name__ == "__main__":
    load_commands("general")
    load_commands("currency")

#
# Define bot events
#

@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user.name}")
    log.info(f"Discord.py API version: {disnake.__version__}")
    log.info(f"Python version: {platform.python_version()}")
    log.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    await status_task()

# Setup the game status task of the bot
async def status_task():
    await bot.change_presence(activity=disnake.Game(
        "github.com/hmccarty/arc_assistant"
    ))

@bot.event
async def on_message(msg: disnake.Message):
    if msg.author == bot.user or msg.author.bot:
        return

    if msg.guild == None:
        # Check if user is in arcdle game

        arcdle = ARCdleModel.get_member_active_game(msg.author.id)
        if arcdle is not None:
            game = bot.get_cog("game")
            if game is not None:
                await game.handle_message(msg, arcdle)
                return

        # If not, assume user is verifying
        verification = bot.get_cog("verification")
        if verification is not None:
            await verification.handle_message(msg)
            return

    await bot.process_commands(msg)

# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx: commands.Context):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    log.info(
        (f"Executed {executedCommand} command in {ctx.guild.name} ",
         f"(ID: {ctx.message.guild.id}) by {ctx.message.author} ",
         f"(ID: {ctx.message.author.id})"))


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(ctx: commands.Context,
    error: commands.CommandError):

    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        desc = "You can use this command again in " \
            f"{f'{round(hours)} hours' if round(hours) > 0 else ''} " \
            f"{f'{round(minutes)} minutes' if round(minutes) > 0 else ''} " \
            f"{f'{round(seconds)} seconds' if round(seconds) > 0 else ''}."
        embed = disnake.Embed(
            title="Hey, please slow down!",
            description=desc,
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        if len(error.missing_perms) == 0:
            desc = "You are missing the permissions to execute this command!"
        else:
            desc = "You are missing the permission `" + ", ".join(
                    error.missing_perms) + "` to execute this command!"
        embed = disnake.Embed(
            title="Error!",
            description=desc,
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument) or \
        isinstance(error, commands.MemberNotFound) or \
        isinstance(error, commands.CommandNotFound) or \
        isinstance(error, commands.UserInputError) or \
        isinstance(error, commands.NoPrivateMessage) or \
        isinstance(error, exceptions.InternalSQLError):
        embed = disnake.Embed(
            title="Error!",
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    raise error


# Run the bot with the token
bot.run(config["bot_token"])
