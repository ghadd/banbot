import telebot 
from utils import *
from config import *
from threading import Timer
import sys

bot = telebot.TeleBot(token = TOKEN, threaded = False)

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

@bot.message_handler(commands = ['ban'], func = lambda msg: is_admin(msg))
def ban_user(msg):
    if not msg.reply_to_message:
        bot.delete_message(msg.chat.id, msg.message_id)
        return None

    if msg.reply_to_message.from_user.id in [DAN, PUFF]:
        return None

    reason = ""
    if not msg.text.startswith("/ban@lpnu_banbot"):
        reason = msg.text[5:]
    else:
        reason = msg.text[16:]
    
    for i in get_chats():
        bot.kick_chat_member(int(i[0]), msg.reply_to_message.from_user.id, 0)
        to_delete = (bot.send_message(msg.chat.id,
        "[{}](tg://user?id={}) banned [{}](tg://user?id={}) for ".format(
            msg.from_user.first_name, 
            msg.from_user.id,
            msg.reply_to_message.from_user.first_name, 
            msg.reply_to_message.from_user.id
            ) + reason, 
            parse_mode = "Markdown"
        ).message_id)

    bot.forward_message(
        LOG_CHAT, 
        msg.chat.id, 
        msg.reply_to_message.message_id
    )
    bot.send_message(
        LOG_CHAT, 
        "reason: " + reason
    )
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
    try:
        timer = Timer(60, lambda msg: bot.delete_message(msg.chat.id, to_delete), [msg])
        timer.start()
    except:
        pass
        
@bot.message_handler(commands = ['unban'])
def unban(msg):
    if not msg.text.startswith("/unban@lpnu_banbot"):
        for i in get_chats():
            try:
                bot.unban_chat_member(int(i[0]), int(msg.text[7:]))
            except:
                bot.send_message(msg.chat.id, "Error")
                return
    else:
        try:
            bot.unban(int(i[0]), int(msg.text[18:]))
        except:
            bot.send_message(msg.chat.id, "Error")
            return

    bot.reply_to(
                msg, 
                "Unbanned"
            )

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