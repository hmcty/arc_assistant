""""
Created by Harrison McCarty - Autonomous Robotics Club of Purdue

Description:
Enables on-server currency.
"""

import json
import os
import sys
import sqlite3
from web3 import Web3, exceptions

import discord
from discord.ext import commands

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

if not os.path.isfile("abi.json"):
    sys.exit("'abi.json' not found! Please add it and try again.")
else:
    with open("abi.json") as file:
        abi = file.read()

class Currency(commands.Cog, name="currency"):
    def __init__(self, bot):
        self.bot = bot
        self.w3 = Web3(Web3.HTTPProvider(config["rpc"]))

        with self.open_db() as c:
            c.execute("CREATE TABLE IF NOT EXISTS currency(member INT, balance REAL, wallet string)")

    def open_db(self):
        return sqlite3.connect(config["db"], timeout=10)

    def get_w3(self):
        if not self.w3.isConnected():
            self.w3 = Web3(Web3.HTTPProvider(config["rpc"]))
        return self.w3

    @commands.command(name="setwallet")
    async def setwallet(self, context, wallet: str):
        """
        Sets a member's wallet address.
        """

        member_id = context.message.author.id
        ref_id = "<@" + str(member_id) + ">"
        try:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM currency WHERE member=(?)", (member_id,)
                    ).fetchone()

                if result is None:
                    c.execute("INSERT INTO currency VALUES (?, ?, ?)", (member_id, 0, wallet))
                else:
                    c.execute(
                            "UPDATE currency SET wallet=(?) WHERE member=(?)",
                            (wallet, result[0]),
                        )
                await context.send(f"{ref_id} set wallet to {wallet}")
        except sqlite3.Error as e:
            await context.send(f"Unable to set wallet address: {e.args[0]}")

    @commands.command(name="printwallet")
    async def printwallet(self, context):
        """
        Prints members current wallet
        """

        member_id = context.message.author.id
        ref_id = "<@" + str(member_id) + ">"
        try:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM currency WHERE member=(?)", (member_id,)
                    ).fetchone()

                if result is None:
                    await context.send(f"{ref_id} no wallet address set")
                else: 
                    await context.send(f"{ref_id} wallet address is {result[2]}")
        except sqlite3.Error as e:
            await context.send(f"Unable to set wallet address: {e.args[0]}")

    @commands.command(name="balance")
    async def balance(self, context):
        """
        Prints current balance of owed and owned ARC coins.
        """
        name = context.message.author.name
        member_id = context.message.author.id
        ref_id = "<@" + str(member_id) + ">"

        wallet = ""
        balance = 0.0
        with self.open_db() as c:
            result = c.execute(
                "SELECT * FROM currency WHERE member=(?)", (member_id,)
            ).fetchone()

            if result is not None:
                balance = result[1]
                wallet = result[2]

        if wallet != "":
            w3 = self.get_w3()
            contract = w3.eth.contract(address=config["eth_contract"], abi=abi)
            result = contract.functions.balanceOf(wallet).call()
            balance += (float(result)/100.0)
        await context.send(ref_id + " has " + str(balance) + " ARC coins")

    @commands.command(name="export")
    async def export(self, context):
        """
        Exports member tokens to saved wallet address.
        """
        
        member_id = context.message.author.id
        ref_id = "<@" + str(member_id) + ">"
        try:
            with self.open_db() as c:
                result = c.execute(
                        "SELECT * FROM currency WHERE member=(?)", (member_id,)
                    ).fetchone()

                if result is None:
                    await context.send(f"{ref_id} no wallet address set, use .setwallet <wallet>")
                else:
                    balance = int(result[1] * 100)
                    address = result[2]

                    w3 = self.get_w3()
                    contract = w3.eth.contract(address=config["eth_contract"], abi=abi)

                    transact = contract.functions.transfer(
                        address,
                        balance,
                    ).buildTransaction({
                        'chainId': w3.eth.chainId,
                        'nonce': w3.eth.get_transaction_count(config["eth_address"]),
                        'gas': 0,
                        'maxFeePerGas': 2000000000,
                        'maxPriorityFeePerGas': 1000000000,
                        'from': config["eth_address"],
                    })

                    gas = w3.eth.estimate_gas(transact)
                    transact.update({'gas': gas})

                    hash = None
                    with open(config["eth_keyfile"]) as keyfile:
                        enc_key = keyfile.read()
                        private_key = w3.eth.account.decrypt(enc_key, config["eth_password"])
                        signed = w3.eth.account.sign_transaction(transact, private_key=private_key)
                        hash = w3.eth.send_raw_transaction(signed.rawTransaction)

                    if hash is not None and w3.eth.wait_for_transaction_receipt(hash) is not None:
                        c.execute(
                            "UPDATE currency SET balance=(?) WHERE member=(?)",
                            (0, result[0]),
                        )
                        await context.send(f"{ref_id} successfully moved {result[1]} coins to wallet 0x{result[0]}")
                    else:
                        await context.send(f"{ref_id} failed to move coins to wallet: 0x{result[0]}")
        except sqlite3.Error as e:
            await context.send(f"{ref_id} failed to export coins: {e.args[0]}")
        except exceptions.TransactionNotFound:
            await context.send(f"{ref_id} failed to move coins to wallet: {result[0]}")

    @commands.command(name="thanks")
    async def thanks(self, context, member: discord.Member):
        """
        Pays an ARC member for their help.
        """

        if member.id == context.message.author.id:
            refid = "<@" + str(context.message.author.id) + ">"
            await context.send(refid + " stop trying to print ARC coins.")
            return

        try:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM currency WHERE member=(?)", (member.id,)
                ).fetchone()
                if result is None:
                    c.execute("INSERT INTO currency VALUES (?, ?)", (member.id, 1))
                else:
                    c.execute(
                        "UPDATE currency SET balance=(?) WHERE member=(?)",
                        (result[1] + 1, result[0]),
                    )

                refid = "<@" + str(member.id) + ">"
                await context.send("Gave +1 ARC Coins to {}".format(refid))
        except sqlite3.Error as e:
            await context.send("Unable to produce coin: {}".format(e.args[0]))

    @commands.command(name="leaderboard")
    async def leaderboard(self, context):
        """
        Prints top 5 members with most amount of ARC coins.
        """

        with self.open_db() as c:
            results = c.execute(
                "SELECT * FROM currency ORDER BY balance desc LIMIT 5"
            ).fetchall()

        if len(results) == 0:
            leaderboard = "Everybody is broke"
        elif context.guild is not None:
            leaderboard = "**ARC Coin Leaderboard**\n"
            pos = 1
            for result in results:
                member = context.guild.get_member(result[0])
                if member is not None:
                    if member.nick is not None:
                        name = member.nick
                    else:
                        name = member.name

                    if result[1] == 1:
                        leaderboard += "{}: {} with {} coin\n".format(
                            pos, name, result[1]
                        )
                    else:
                        leaderboard += "{}: {} with {} coins\n".format(
                            pos, name, result[1]
                        )
                pos += 1
        else:
            leaderboard = "Command can only be used in a guild."
        await context.send(leaderboard)

    @commands.command(name="set")
    async def set(self, context, member: discord.Member, amount: float):
        """
        Sets the balance of a member (OWNER-ONLY COMMAND).
        """

        if member is None:
            refid = "<@" + str(context.message.author.id) + ">"
            await context.send(refid + " you didn't say who you're sending money too.")
        elif context.message.author.id in config["owners"]:
            with self.open_db() as c:
                result = c.execute(
                    "SELECT * FROM currency WHERE member=(?)", (member.id,)
                ).fetchone()
                if result is None:
                    c.execute("INSERT INTO currency VALUES (?, ?)", (member.id, amount))
                else:
                    c.execute(
                        "UPDATE currency SET balance=(?) WHERE member=(?)",
                        (amount, member.id),
                    )

            await context.send(
                "{} set {} balance to {}".format(
                    "<@" + str(context.message.author.id) + ">",
                    "<@" + str(member.id) + ">",
                    amount,
                )
            )
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Currency(bot))
