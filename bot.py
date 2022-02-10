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

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.emojis = True
intents.bans = True
intents.guild_typing = False
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.guild_messages = True
intents.guild_reactions = True
intents.integrations = True
intents.invites = True
intents.voice_states = False
intents.webhooks = False

Privileged Intents (Needs to be enabled on dev page), please use them only if you need them:
intents.presences = True
intents.members = True
"""

intents = discord.Intents.default()
intents.members = True
intents.reactions = True

bot = Bot(command_prefix=config["bot_prefix"], intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"Discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    await status_task()

# Setup the game status task of the bot
async def status_task():
    await bot.change_presence(activity=discord.Game(
        "github.com/hmccarty/arc_assistant"
    ))

# Removes the default help command
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")

@bot.event
async def on_message(msg: discord.Message):
    if msg.author == bot.user or msg.author.bot:
        return

    if msg.guild == None:
        # Check if user is in arcdle game
        currency = bot.get_cog("currency")
        if currency is not None:
            if await currency.in_arcdle_game(msg.author.id):
                await currency.handle_message(msg)
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
    print(
        f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")


# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        if len(error.missing_perms) == 0:
            embed = discord.Embed(
                title="Error!",
                description="You are missing the permissions to execute this command!",
                color=0xE02B2B
            )
        else:
            embed = discord.Embed(
                title="Error!",
                description="You are missing the permission `" + ", ".join(
                    error.missing_perms) + "` to execute this command!",
                color=0xE02B2B
            )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument) or \
        isinstance(error, commands.MemberNotFound) or \
        isinstance(error, commands.CommandNotFound) or \
        isinstance(error, commands.UserInputError):
        embed = discord.Embed(
            title="Error!",
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await ctx.send(embed=embed)
    raise error


# Run the bot with the token
bot.run(config["bot_token"])
