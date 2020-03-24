import telebot 
import telebot
import sqlite3
from threading import Timer
import sys

TOKEN = '1149280632:AAGofBLZh-W3h77dd0xj4ikgWAFUUL6_BkA'
DAN = 662834330
PUFF = 781222163
LOG_CHAT = -434708426
to_delete = []
bot = telebot.TeleBot(token = TOKEN, threaded = False)


class DataConn:
    def __init__(self, db_name):
        self.db_name = db_name
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise

def is_admin(msg):
    if not msg:
        return False
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM `admins` WHERE `user_id` = "{}"'.format(
            msg.from_user.id
        )
        cursor.execute(query)
        r = cursor.fetchone()
        return r is not None

def add_admin(msg):
    if not msg:
        return False
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'INSERT INTO `admins` (`user_id`) VALUES("{}")'.format(
            msg.from_user.id
        ) 
        cursor.execute(query)
        conn.commit()
        return True

def remove_admin(msg):
    if not msg:
        return False
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'DELETE FROM `admins` WHERE `user_id` = "{}"'.format(
            msg.from_user.id
        ) 
        cursor.execute(query)
        conn.commit()
        return True

def is_registered(msg):
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM `chats` WHERE `chat_id` = "{}"'.format(
            msg.chat.id
        )
        cursor.execute(query)
        r = cursor.fetchone()
        return r is not None

def reg(msg):
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'INSERT INTO `chats` (`chat_id`) VALUES("{}")'.format(
            msg.chat.id
        ) 
        cursor.execute(query)
        conn.commit()

def unreg(msg):
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'DELETE FROM `chats` WHERE `chat_id` = "{}"'.format(
            msg.chat.id
        ) 
        cursor.execute(query)
        conn.commit()

def get_chats():
    with DataConn("db.db") as conn:
        cursor = conn.cursor()
        query = 'SELECT * FROM `chats`'
        cursor.execute(query)
        r = cursor.fetchall()
        return r

@bot.message_handler(commands = ['start'])
def start(msg):
    bot.send_message(
        msg.chat.id, 
        "I can ban fuckers :)"
    )

@bot.message_handler(commands = ['reg'], func = lambda msg: is_admin(msg))
def reg_chat(msg):
    if '-rm' in msg.text:
        txt = "Removed chat successfully" if is_registered(msg) else "Chat is not registered yet"
        unreg(msg)
        bot.reply_to(
            msg, 
            txt
        )
    else:
        txt = "Added chat successfully" if not is_registered(msg) else "Chat is already registered"
        reg(msg)
        bot.reply_to(
            msg, 
            txt
        )

@bot.message_handler(commands = ['adm'], func = lambda msg: msg.from_user.id in [DAN, PUFF])
def adm(msg):
    if '-rm' in msg.text:
        txt = "Removed admin successfully" if is_admin(msg.reply_to_message) else "User is not an admin"
        if remove_admin(msg.reply_to_message):
            bot.reply_to(
                msg, 
                txt
            )
        else:
            bot.reply_to(
                msg, 
                "Try replying to some message"
            )
    else:
        txt = "Added admin successfully" if not is_admin(msg.reply_to_message) else "User is already an admin"
        if add_admin(msg.reply_to_message):
            bot.reply_to(
                msg, 
                txt
            )
        else:
            bot.reply_to(
                msg, 
                "Try replying to some message"
            )

@bot.message_handler(commands = ['ban'])
def ban_user(msg):
    if not msg.reply_to_message:
        bot.delete_message(msg.chat.id, msg.message_id)
        return None

    reason = ""
    if msg.text.startswith("/ban"):
        reason = msg.text[5:]
    else:
        reason = msg.text[16:]
    
    for i in get_chats():
        bot.kick_chat_member(int(i), msg.reply_to, 0)
        print(bot.send_message(msg.chat.id,
            "[{}](tg://user?id={}) banned [{}](tg://user?id={}) for ".format(
                msg.from_user.first_name, 
                msg.from_user.id,
                msg.reply_to_message.from_user.first_name, 
                msg.reply_to_message.from_user.id
                ) + reason, 
                parse_mode = "Markdown"
        )
        )
        # timer = Timer(5, lambda msg: bot.delete_message(msg.chat.id, msg.message_id))
        # timer.start()
        

@bot.message_handler(commands = ['getchats'], func = lambda msg: is_admin(msg))
def getchats(msg):
    txt = ""
    for i in get_chats():
        txt += str(i) + '\n'
    bot.reply_to(
        msg, 
        txt
        )

bot.polling(none_stop = True)