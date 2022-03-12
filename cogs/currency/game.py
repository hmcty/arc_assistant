""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Enables on-server currency.
"""

import json
import os
import sys
import sqlite3
import typing
import random
from datetime import date

import disnake
from disnake.ext import commands, tasks

from helpers import arcdle
from helpers.db_manager import MemberModel, CurrencyModel, ARCdleModel, DailyModel

from exceptions import InternalSQLError

ARCDLE_WIN_AMT = 2.5
ARCDLE_LOSE_AMT = 1.0
DAILY_LAMBDA = 2.5

class Game(commands.Cog, name="game"):
    def __init__(self, bot):
        self.bot = bot
        self.arcdle_sol = arcdle.pick_solution()
        self.emojis = {}

    def get_emoji(self, letter: str):
        if letter not in self.emojis:
            for emoji in self.bot.emojis:
                if emoji.name == f"g_{letter}":
                    self.emojis[letter] = emoji
                    break
        return self.emojis[letter]

    @tasks.loop(hours=1)
    async def check_wipe(self):
        now = datetime.utcnow()

        # 12am EST in UTC
        if now.hour == 5:
            ARCdleModel.clear_games()
        
    async def handle_message(self, msg: disnake.Message, arcdle_game: ARCdleModel):
        """
        Called when a direct message is received for arcdle.
        """

        msg_content = msg.content.strip().lower()
        if len(msg_content) == 5 and msg_content.isalpha():
            visible = arcdle_game.visible
            hidden = arcdle_game.hidden
            status = arcdle_game.status

            sol = self.arcdle_sol

            prev_visible_guesses = visible.split(",")
            prev_hidden_guesses = hidden.split(",")

            hidden_guess = ""
            visible_guess = ""
            correct_cnt = 0

            # Remove perfect matches
            for i in range(5):
                if msg_content[i] == self.arcdle_sol[i]:
                    sol = sol.replace(msg_content[i], "", 1)

            # Display partial and perfect matches
            for i in range(5):
                if msg_content[i] == self.arcdle_sol[i]:
                    correct_cnt += 1
                    visible_guess += f"{self.get_emoji(msg_content[i])} "
                    hidden_guess += ":green_square: "
                elif msg_content[i] in sol:
                    sol = sol.replace(msg_content[i], "", 1)
                    visible_guess += f":regional_indicator_{msg_content[i]}: "
                    hidden_guess += ":yellow_square: "
                else:
                    visible_guess += f"{msg_content[i]} "
                    hidden_guess += ":black_large_square: "

            if prev_visible_guesses[0] != "":
                visible_guesses = prev_visible_guesses + [visible_guess]
            else:
                visible_guesses = [visible_guess]
            
            if prev_hidden_guesses[0] != "":
                hidden_guesses = prev_hidden_guesses + [hidden_guess]
            else:
                hidden_guesses = [hidden_guess]

            status = 0
            if correct_cnt == 5:
                status = 1
            elif len(visible_guesses) == 6:
                status = 2

            winning_amt = 0.0
            member_id = msg.author.id
            if status == 1:
                winning_amt = ARCDLE_WIN_AMT
                board_desc = f"<@{member_id}> guessed in {len(visible_guesses)} attempt(s), " \
                    f"earning {winning_amt} ARC coins\n\n"
            elif status == 2:
                winning_amt = ARCDLE_LOSE_AMT
                board_desc = f"<@{member_id}> failed to guess in {len(visible_guesses)} attempt(s), " \
                    f"earning {winning_amt} ARC coins\n\n"
            else:
                board_desc = f"{6-len(visible_guesses)}/6 guesses remain\n\n"

            if status != 0:
                guild_id, channel_id = arcdle_game.get_origin()
                balance = CurrencyModel.get_balance_or_create(msg.author.id)
                CurrencyModel.update_balance(msg.author.id, balance + winning_amt)

                public_desc = board_desc
                for i in range(len(hidden_guesses)):
                    public_desc += hidden_guesses[i]
                    if i < 5:
                        public_desc += "\n\n"

                guild = self.bot.get_guild(guild_id)
                public = disnake.Embed(title=f"{msg.author.name}'s ARCdle", description=public_desc)
                await guild.get_channel(channel_id).send(embed=public)

            for i in range(len(visible_guesses)):
                board_desc += visible_guesses[i]
                if i < 5:
                    board_desc += "\n\n"

            if status == 0:
                for i in range(len(visible_guesses), 6):
                    board_desc += "\_ \_ \_ \_ \_"
                    if i < 5:
                        board_desc += "\n\n"
            else:
                board_desc += f"\n\n The word was {self.arcdle_sol}"
            board = disnake.Embed(title="ARCdle", description=board_desc)

            old_board = await msg.channel.fetch_message(arcdle_game.message_id)
            await old_board.edit(embed=board)

            visible_guesses = ",".join(visible_guesses)
            hidden_guesses = ",".join(hidden_guesses)

            arcdle_game.update(visible_guesses, hidden_guesses, status)
        else:
            await msg.channel.send("Guess must be a 5 letter word.")

    @commands.command(name="daily")
    async def daily(self, ctx: commands.Context):
        """
        Roll for a daily source of ARC coins.
        """

        if DailyModel.was_redeemed(ctx.author.id):
            await ctx.reply("You've already redeemed today, come back tomorrow")
        else:
            amt = round(random.expovariate(DAILY_LAMBDA), 2)
            balance = CurrencyModel.get_balance_or_create(ctx.author.id)
            CurrencyModel.update_balance(ctx.author.id, balance + amt)
            DailyModel.redeem(ctx.author.id)
            await ctx.reply(f"Congrats! You won {amt} ARC coins")
            

    @commands.command(name="arcdle")
    async def arcdle(self, ctx: commands.Context):
        """
        Starts a game of arcdle.
        """

        arcdle_game = ARCdleModel.get_member_recent_game(ctx.author.id)

        # Handle already started games
        if arcdle_game is not None:
            if arcdle_game.status == 0:
                await ctx.reply("You've already started a game, check your DMs")
            else:
                await ctx.reply("You've already played today, come back tomorrow")
            return
        else:
            if ARCdleModel.get_num_games() == 0:
                self.arcdle_sol = arcdle.pick_solution()
        
        # Start a new game
        board_desc = "6/6 guesses remain \n\n"
        for i in range(6):
            board_desc += "\_ \_ \_ \_ \_"
            if i < 5:
                board_desc += "\n\n"
        board = disnake.Embed(title="ARCdle", description=board_desc)
        message = await ctx.message.author.send(embed=board)
        ARCdleModel.create_game(ctx.author.id, ctx.guild.id, ctx.channel.id, message.id)

def setup(bot):
    bot.add_cog(Game(bot))
