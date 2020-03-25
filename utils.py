import telebot
import sqlite3

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