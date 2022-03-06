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
            "guild_id INTEGER, balance INTEGER, verified INTEGER, code INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS member_arcdle(arcdle_rowid INTEGER PRIMARY KEY, " \
            "member_id INTEGER, guild_id INTEGER, channel_id INTEGER) WITHOUT ROWID")

        # Verification table
        c.execute("CREATE TABLE IF NOT EXISTS verification(guild_id INT, " \
            "role_id INT, domain TEXT)")

        # Role menu table
        c.execute("CREATE TABLE IF NOT EXISTS rolemenu(message_id INTEGER, " \
            "guild_id INTEGER, role TEXT, emoji TEXT)")

        # ARCdle table
        c.execute("CREATE TABLE IF NOT EXISTS arcdle(message_id INTEGER, visible TEXT, " \
            "hidden TEXT, status INT)")

        # Backlog table
        c.execute("CREATE TABLE IF NOT EXISTS backlog(id INTEGER PRIMARY KEY, item TEXT)")

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
    def get_all(member_id: int):
        with open_db() as c:
            results = c.execute(
                "SELECT rowid, * FROM member WHERE member_id=(?)",
                (member_id,)
            ).fetchall()

            if results:
                members = []
                for result in results:
                    rowid, _, guild_id, balance, verified, code = result
                    members.append(
                        MemberModel(rowid, member_id, guild_id, balance, verified, code))
                return members
            return []


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
            result = c.execute(
                """
                DELETE FROM arcdle
                """,
            )

    @staticmethod
    def get_member_active_game(member_id: int):
        with open_db() as c:
            result = c.execute(
                """
                SELECT rowid, message_id, visible, hidden, status
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
