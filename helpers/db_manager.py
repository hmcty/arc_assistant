import sqlite3
import os
import sys
import json

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

def open_db():
    return sqlite3.connect(config["db"], timeout=10)

#
# Setup initial database
#

with open_db() as c:
    # Member tables
    c.execute("CREATE TABLE IF NOT EXISTS member(member_id INTEGER, " \
        "guild_id INTEGER, balance INTEGER, verified INTEGER, code INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS member_arcdle(member_rowid INTEGER PRIMARY KEY, " \
        "arcdle_rowid INTEGER) WITHOUT ROWID")

    # Role menu table
    c.execute("CREATE TABLE IF NOT EXISTS rolemenu(message_id INTEGER PRIMARY KEY, " \
        "guild_id INTEGER, role TEXT, emoji TEXT) WITHOUT ROWID")

    # ARCdle table
    c.execute("CREATE TABLE IF NOT EXISTS arcdle(visible TEXT, hidden TEXT, status INT)")

#
# Define database models
#

class MemberModel(object):
    @staticmethod
    def get_or_create(member_id: int, guild_id: int):
        try:
            con = open_db()
            c = con.cursor()

            result = c.execute(
                "SELECT rowid, * FROM member WHERE member_id=(?) AND guild_id=(?)",
                (member_id, guild_id)
            ).fetchone()

            if result is not None:
                rowid, _, _, balance, verified, code = result
                return MemberModel(rowid, member_id, guild_id, balance, verified, code)
            else:
                c.execute(
                    "INSERT INTO member VALUES (?, ?, ?, ?, ?)",
                    (member_id, guild_id, 0, 0, 0)
                )
                con.commit()
                con.close()

                return MemberModel(c.lastrowid, member_id, guild_id, 0, 0, 0)
        except sqlite3.Error as e:
            return None

    @staticmethod
    def get_richest(n: int = 10):
        members = []
        with open_db() as c:
            results = c.execute(
                "SELECT rowid, * FROM member ORDER BY balance desc LIMIT (?)",
                (n,)
            ).fetchall()

            for i in results:
                rowid, member_id, guild_id, balance, verified, code = i
                members.append(MemberModel(rowid, member_id, guild_id, balance, verified, code))
        return members

    def __init__(self, rowid: int, member_id: int, guild_id: int, balance: int, verified: int, code: int):
        self.rowid = rowid
        self.member_id = member_id
        self.guild_id = guild_id
        self.balance = balance
        self.verified = verified
        self.code = code

    def get_or_create_arcdle(self):
        result = None
        with open_db() as c:
            result = c.execute(
                "SELECT * FROM member_arcdle WHERE member_rowid=(?)",
                (self.rowid,)
            ).fetchone()

        if result is None:
            con = open_db()
            c = con.cursor()
            result = ("", "", 0)
            c.execute(
                "INSERT INTO arcdle VALUES (?, ?, ?)",
                result
            )
            con.commit()

            arcdle_rowid = c.lastrowid
            c.execute(
                "INSERT INTO member_arcdle VALUES (?, ?)",
                (self.rowid, arcdle_rowid)
            )
            con.commit()
            con.close()
            return dbARCdle.get(arcdle_rowid)
        else:
            return dbARCdle.get(result[1])

    def update_balance(self, balance: int):
        with open_db() as c:
            c.execute(
                "UPDATE member SET balance=(?) WHERE rowid=(?)",
                (balance, self.rowid)
            )
            self.balance = balance

    def update_verified(self, verified: int):
        with open_db() as c:
            c.execute(
                "UPDATE member SET verified=(?) WHERE rowid=(?)",
                (verified, self.rowid)
            )
            self.verified = verified

    def update_code(self, code: int):
        with open_db() as c:
            c.execute(
                "UPDATE member SET code=(?) WHERE rowid=(?)",
                (code, self.rowid)
            )
            self.code = code


class dbARCdle(object):
    @staticmethod
    def get(self, rowid: int):
        pass

    def __init__(self, game_id: int, hidden_msg: str, visible_msg: str, status: int):
        self.game_id = game_id
        self.hidden_msg = hidden_msg
        self.visible_msg = visible_msg
        self.status = status

class dbRoleMenu(object):
    @staticmethod
    def get(self, message_id: int):
        pass