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
    c.execute("CREATE TABLE IF NOT EXISTS member_arcdle(arcdle_rowid INTEGER PRIMARY KEY, " \
        "member_id INTEGER, guild_id INTEGER, channel_id INTEGER) WITHOUT ROWID")

    # Role menu table
    c.execute("CREATE TABLE IF NOT EXISTS rolemenu(message_id INTEGER PRIMARY KEY, " \
        "guild_id INTEGER, role TEXT, emoji TEXT) WITHOUT ROWID")

    # ARCdle table
    c.execute("CREATE TABLE IF NOT EXISTS arcdle(message_id INTEGER, visible TEXT, " \
        "hidden TEXT, status INT)")

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


class ARCdleModel(object):
    @staticmethod
    def get(self, rowid: int):
        pass

    @staticmethod
    def get_member_active_game(member_id: int):
        with open_db() as c:
            result = c.execute(
                """
                SELECT rowid, message_id, hidden, visible, status
                FROM arcdle
                INNER JOIN member_arcdle on member_arcdle.arcdle_rowid = arcdle.rowid
                WHERE status=0 AND member_id=(?)
                """,
                (member_id,)
            ).fetchone()
            if result is None:
                return None
            
            rowid, message_id, hidden, visible, status = result
            return ARCdleModel(rowid, message_id, hidden, visible, status)

    @staticmethod
    def get_member_recent_game(member_id: int):
        with open_db() as c:
            result = c.execute(
                """
                SELECT rowid, message_id, hidden, visible, status
                FROM arcdle
                INNER JOIN member_arcdle on member_arcdle.arcdle_rowid = arcdle.rowid
                WHERE member_id=(?)
                ORDER BY rowid DESC
                """,
                (member_id,)
            ).fetchone()
            if result is None:
                return None
            
            rowid, message_id, hidden, visible, status = result
            return ARCdleModel(rowid, message_id, hidden, visible, status)

    @staticmethod
    def create_game(member_id: int, guild_id: int,
        channel_id: int, message_id: int):
        con = open_db()
        c = con.cursor()
        c.execute(
            "INSERT INTO arcdle VALUES (?, ?, ?, ?)",
            (message_id, "", "", 0)
        )
        con.commit()

        arcdle_rowid = c.lastrowid
        c.execute(
            "INSERT INTO member_arcdle VALUES (?, ?, ?, ?)",
            (arcdle_rowid, member_id, guild_id, channel_id)
        )
        con.commit()
        con.close()
        return ARCdleModel.get_member_active_game(member_id)

    def __init__(self, rowid: int, message_id: int, hidden: str, visible: str, status: int):
        self.rowid = rowid
        self.message_id = message_id
        self.hidden = hidden
        self.visible = visible
        self.status = status

    def get_origin(self):
        with open_db() as c:
            result = c.execute(
                """
                SELECT guild_id, channel_id
                FROM arcdle
                INNER JOIN member_arcdle on member_arcdle.arcdle_rowid = arcdle.rowid
                WHERE arcdle.rowid=(?)
                """,
                (self.rowid,)
            ).fetchone()
            return result

    def update(self, hidden: str, visible: str, status: int):
        with open_db() as c:
            c.execute(
                """
                UPDATE arcdle SET visible=(?), hidden=(?), status=(?)
                WHERE rowid=(?);
                """,
                (visible, hidden, status, self.rowid),
            )

class dbRoleMenu(object):
    @staticmethod
    def get(self, message_id: int):
        pass