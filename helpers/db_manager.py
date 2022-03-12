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

def init_db():
    with open_db() as c:
        # Member tables
        c.execute("CREATE TABLE IF NOT EXISTS member(member_id INTEGER, " \
            "guild_id INTEGER, verified INTEGER, code INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS member_arcdle(arcdle_rowid INTEGER PRIMARY KEY, " \
            "member_id INTEGER, guild_id INTEGER, channel_id INTEGER) WITHOUT ROWID")

        # Currency table
        c.execute("CREATE TABLE IF NOT EXISTS currency(member_id INTEGER PRIMARY KEY, balance REAL)")

        # Verification table
        c.execute("CREATE TABLE IF NOT EXISTS verification(guild_id INT, " \
            "role_id INT, domain TEXT)")

        # Role menu table
        c.execute("CREATE TABLE IF NOT EXISTS rolemenu(message_id INTEGER, " \
            "guild_id INTEGER, role TEXT, emoji TEXT)")

        # ARCdle table
        c.execute("CREATE TABLE IF NOT EXISTS arcdle(message_id INTEGER, visible TEXT, " \
            "hidden TEXT, status INT)")

        # Daily ARCoin table
        c.execute("CREATE TABLE IF NOT EXISTS daily(member_id INTEGER PRIMARY KEY)")

        # Backlog table
        c.execute("CREATE TABLE IF NOT EXISTS backlog(id INTEGER PRIMARY KEY, item TEXT)")

        # Calendar table
        c.execute("CREATE TABLE IF NOT EXISTS calendar(guild_id INTEGER, " \
            "channel_id INTEGER, calendar_id TEXT)")

        # Bounty table
        c.execute("CREATE TABLE IF NOT EXISTS bounty(title TEXT, " \
            "owner_id INT, guild_id INT, channel_id INT, message_id INT, amt REAL)")

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

            if result:
                rowid, _, _, verified, code = result
                return MemberModel(rowid, member_id, guild_id, verified, code)
            else:
                c.execute(
                    "INSERT INTO member VALUES (?, ?, ?, ?)",
                    (member_id, guild_id, 0, 0)
                )
                con.commit()
                con.close()

                return MemberModel(c.lastrowid, member_id, guild_id, 0, 0)
        except sqlite3.Error:
            return None

    @staticmethod
    def get_all(member_id: int):
        with open_db() as c:
            results = c.execute(
                "SELECT rowid, * FROM member WHERE member_id=(?)",
                (member_id,)
            ).fetchall()

            if results:
                members = []
                for result in results:
                    rowid, _, guild_id, verified, code = result
                    members.append(
                        MemberModel(rowid, member_id, guild_id, verified, code))
                return members
            return []

    @staticmethod
    def get_richest(guild_id: int, n: int = 10):
        members = []
        with open_db() as c:
            results = c.execute(
                """
                SELECT member.rowid, member.member_id, guild_id, verified, code FROM member
                JOIN currency ON member.member_id = currency.member_id
                WHERE member.guild_id = (?)
                ORDER BY balance desc LIMIT (?)
                """,
                (guild_id, n)
            ).fetchall()

            for i in results:
                rowid, member_id, guild_id, verified, code = i
                members.append(MemberModel(rowid, member_id, guild_id, verified, code))
        return members

    def __init__(self, rowid: int, member_id: int, guild_id: int, verified: int, code: int):
        self.rowid = rowid
        self.member_id = member_id
        self.guild_id = guild_id
        self.verified = verified
        self.code = code

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

class CurrencyModel(object):
    @staticmethod
    def get_balance_or_create(member_id: int):
        with open_db() as c:
            result = c.execute(
                "SELECT * FROM currency WHERE member_id = (?)",
                (member_id,)
            ).fetchone()
            
            if result is None:
                balance = 0.0
                c.execute(
                    "INSERT INTO currency VALUES (?, ?)",
                    (member_id, balance)
                )
            else:
                balance = result[1]

            return balance
    
    @staticmethod
    def update_balance(member_id: int, balance: float):
        with open_db() as c:
            c.execute(
                "UPDATE currency SET balance=(?) WHERE member_id=(?)",
                (balance, member_id)
            )

class ARCdleModel(object):
    @staticmethod
    def get_num_games():
        with open_db() as c:
            result = c.execute(
                """
                SELECT COUNT(*)
                FROM arcdle
                """,
            ).fetchone()
        return result[0]

    @staticmethod
    def clear_games():
        with open_db() as c:
            c.execute(
                """
                DELETE FROM arcdle
                """,
            )

    @staticmethod
    def get_member_active_game(member_id: int):
        with open_db() as c:
            result = c.execute(
                """
                SELECT arcdle.rowid, message_id, visible, hidden, status
                FROM arcdle
                INNER JOIN member_arcdle on member_arcdle.arcdle_rowid = arcdle.rowid
                WHERE status=0 AND member_id=(?)
                """,
                (member_id,)
            ).fetchone()
            if result is None:
                return None
            
            rowid, message_id, visible, hidden, status = result
            return ARCdleModel(rowid, message_id, visible, hidden, status)

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
            
            rowid, message_id, visible, hidden, status = result
            return ARCdleModel(rowid, message_id, visible, hidden, status)

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

    def __init__(self, rowid: int, message_id: int, visible: str, hidden: str, status: int):
        self.rowid = rowid
        self.message_id = message_id
        self.visible = visible
        self.hidden = hidden
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

    def update(self, visible: str, hidden: str, status: int):
        with open_db() as c:
            c.execute(
                """
                UPDATE arcdle SET visible=(?), hidden=(?), status=(?)
                WHERE rowid=(?);
                """,
                (visible, hidden, status, self.rowid),
            )

class DailyModel(object):
    @staticmethod
    def redeem(member_id: int):
        if DailyModel.was_redeemed(member_id):
            return
        
        with open_db() as c:
            c.execute("INSERT INTO daily VALUES (?)",
                (member_id,)
            )

    @staticmethod
    def was_redeemed(member_id: int):
        with open_db() as c:
            result = c.execute("SELECT * FROM daily " \
                "WHERE member_id = (?)",
                (member_id,)
            ).fetchone()
            return result is not None

    @staticmethod
    def clear_daily():
        with open_db() as c:
            result = c.execute("DELETE FROM daily")

class RoleMenuModel(object):
    @staticmethod
    def get(message_id: int, guild_id: int):
        with open_db() as c:
            results = c.execute(
                """
                SELECT *
                FROM rolemenu
                WHERE message_id=(?) and guild_id=(?)
                """,
                (message_id, guild_id)
            ).fetchall()
            return list(map(lambda x: RoleMenuModel(x[0], x[1], x[2], x[3]), results))

    @staticmethod
    def add_option(message_id: int, guild_id: int, role: str, emoji: str):
        with open_db() as c:
            c.execute(
                "INSERT INTO rolemenu VALUES (?, ?, ?, ?)",
                (message_id, guild_id, role, emoji)
            )

    @staticmethod
    def delete_menu(message_id: int, guild_id: int):
        with self.open_db() as c:
            c.execute("DELETE FROM rolemenu WHERE message_id=(?) AND guild_id=(?)",
                (message_id, guild_id)
            )

    def __init__(self, message_id: int, guild_id: int, role: str, emoji: str):
        self.message_id = message_id
        self.guild_id = guild_id
        self.role = role
        self.emoji = emoji
        
class BacklogModel(object):
    @staticmethod
    def get_all():
        with open_db() as c:
            results = c.execute("SELECT * FROM backlog").fetchall()
            return list(map(lambda x: BacklogModel(x[0], x[1]), results))

    @staticmethod
    def find_and_remove(item: str):
        with open_db() as c:
            result = c.execute(
                "SELECT * FROM backlog WHERE item LIKE (?)",
                ("%" + item + "%",)
            ).fetchone()
            if result is not None:
                c.execute(
                    "DELETE FROM backlog WHERE id=(?)", (result[0],)
                )
                return True
        return False

    @staticmethod
    def add(item: str):
        with open_db() as c:
            c.execute(
                "INSERT INTO backlog(item) VALUES (?)", (item,)
            )

    def __init__(self, id: int, item: str):
        self.id = id
        self.item = item

class VerificationModel(object):
    @staticmethod
    def configure(guild_id: int, role_id: int, domain: str):
        with open_db() as c:
            c.execute(
                "INSERT OR IGNORE INTO verification (guild_id, role_id, domain) " \
                "VALUES (?, ?, ?)",
                (guild_id, role_id, domain)
            )
            c.execute(
                "UPDATE verification SET role_id = (?), domain = (?) " \
                "WHERE guild_id=(?)",
                (role_id, domain, guild_id)
            )

    @staticmethod
    def get(guild_id: int):
        with open_db() as c:
            result = c.execute(
                """
                SELECT *
                FROM verification
                WHERE guild_id=(?)
                """,
                (guild_id,)
            ).fetchone()
            if result:
                return VerificationModel(guild_id, result[1], result[2])

    def __init__(self, guild_id: int, role_id: int, domain: str):
        self.guild_id = guild_id
        self.role_id = role_id
        self.domain = domain

class CalendarModel(object):
    @staticmethod
    def get_all():
        with open_db() as c:
            results = c.execute("SELECT * FROM calendar").fetchall()
            return list(map(lambda x: CalendarModel(x[0], x[1], x[2]), results))

    @staticmethod
    def get_by_guild(guild_id: int):
        with open_db() as c:
            results = c.execute(
                """
                SELECT *
                FROM calendar
                WHERE guild_id=(?)
                """,
                (guild_id,)
            ).fetchall()
            return list(map(lambda x: CalendarModel(x[0], x[1], x[2]), results))

    @staticmethod
    def get_by_channel(guild_id: int, channel_id: int):
        with open_db() as c:
            results = c.execute(
                """
                SELECT *
                FROM calendar
                WHERE guild_id=(?) AND channel_id=(?)
                """,
                (guild_id, channel_id)
            ).fetchall()
            return list(map(lambda x: CalendarModel(x[0], x[1], x[2]), results))

    @staticmethod
    def get(guild_id: int, channel_id: int, calendar_id: str):
        with open_db() as c:
            result = c.execute(
                """
                SELECT *
                FROM calendar
                WHERE guild_id=(?) AND channel_id=(?)
                AND calendar_id=(?)
                """,
                (guild_id, channel_id, calendar_id)
            ).fetchone()
            if result:
                return CalendarModel(result[0], result[1], result[2])
            else:
                return None

    @staticmethod
    def add(guild_id: int, channel_id: int, calendar_id: str):
        with open_db() as c:
            c.execute(
                "INSERT OR IGNORE INTO calendar (guild_id, channel_id, calendar_id) " \
                "VALUES (?, ?, ?)",
                (guild_id, channel_id, calendar_id)
            )

    def __init__(self, guild_id: int, channel_id: int, calendar_id: str):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.calendar_id = calendar_id

    def remove(self):
        with open_db() as c:
            c.execute(
                "DELETE FROM calendar " \
                "WHERE guild_id=(?) AND channel_id=(?) AND calendar_id=(?)",
                (self.guild_id, self.channel_id, self.calendar_id)
            )

class BountyModel(object):
    @staticmethod
    def get(title: str):
        with open_db() as c:
            result = c.execute(
                "SELECT * FROM bounty WHERE title like (?)",
                (title,)
            ).fetchone()

            if result:
                return BountyModel(result[0], result[1], result[2],
                    result[3], result[4], result[5])
            else:
                return None

    @staticmethod
    def create(title: str, owner_id: int, guild_id: int, channel_id: int,
        message_id: int, amt: float):
        with open_db() as c:
            c.execute(
                "INSERT INTO bounty (title, owner_id, guild_id, channel_id, message_id, amt) " \
                "VALUES (?, ?, ?, ?, ?, ?)",
                (title, owner_id, guild_id, channel_id, message_id, amt)
            )

    def __init__(self, title: str, owner_id: int, guild_id: int, channel_id: int,
        message_id: int, amt: float):
        self.title = title
        self.owner_id = owner_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.amt = amt

    def contribute(self, amt: float):
        with open_db() as c:
            c.execute(
                """
                UPDATE bounty SET amt=(?) WHERE
                "title like (?) AND owner_id=(?)
                """,
                (amt + self.amt, self.title, self.owner_id)
            )
        self.amt += amt

    def complete(self):
        with open_db() as c:
            c.execute(
                """
                DELETE FROM bounty WHERE
                title like (?) AND owner_id=(?)
                """,
                (self.title, self.owner_id)
            )