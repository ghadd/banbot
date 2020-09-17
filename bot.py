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

@bot.message_handler(commands = ['bye'], func = lambda msg: is_admin(msg))
def ban_user(msg):
    if not msg.reply_to_message:
        bot.delete_message(msg.chat.id, msg.message_id)
        return None

    if msg.reply_to_message.from_user.id in [DAN, PUFF]:
        return None

    reason = ""
    if not msg.text.startswith("/bye@lpnu_banbot"):
        reason = msg.text[5:]
    else:
        reason = msg.text[16:]

    bot.forward_message(
        LOG_CHAT, 
        msg.chat.id, 
        msg.reply_to_message.message_id
    )
    bot.send_message(
        LOG_CHAT, 
        "reason: " + reason
    )
    user_to_ban_id = msg.reply_to_message.from_user.id
    to_delete = (bot.send_message(msg.chat.id,
        "[{}](tg://user?id={}) banned [{}](tg://user?id={}) for ".format(
            msg.from_user.first_name, 
            msg.from_user.id,
            msg.reply_to_message.from_user.first_name, 
            msg.reply_to_message.from_user.id
            ) + reason, 
            parse_mode = "Markdown"
        ).message_id)

    chats = [int(i[0]) for i in get_chats()]
    for i in chats:
        try:
            bot.kick_chat_member(i, user_to_ban_id, 0)
            print("OK")
        except:
            print("no roots")

    bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
    bot.delete_message(msg.chat.id, msg.message_id)
    try:
        timer = Timer(60, lambda msg: bot.delete_message(msg.chat.id, to_delete), [msg])
        timer.start()
    except:
        pass
        
@bot.message_handler(commands = ['unbye'])
def unban(msg):
    if not msg.text.startswith("/unbye@lpnu_banbot"):
        id_to_unban = 0
        if msg.reply_to_message:
            id_to_unban = msg.reply_to_message.from_user.id
        else:
            try:
                id_to_unban = int(msg.text[7:])
            except:
                return

        for i in get_chats():
            try:
                bot.unban_chat_member(int(i[0]), id_to_unban)
            except:
                bot.send_message(msg.chat.id, "Error")
                return
    else:
        id_to_unban = 0
        if msg.reply_to_message:
            id_to_unban = msg.reply_to_message.from_user.id
        else:
            id_to_unban = int(msg.text[18:])
            
        for i in get_chats():
            try:
                bot.unban_chat_member(int(i[0]), id_to_unban)
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

@bot.message_handler(commands = ['help'])
def gethelp(msg):
	help_text = """Help text: 
	- /help - display this message
	- /getchats - list chats where bot is registered
	- /bye - (in reply to uses's message) ban user in all registered chats
	- /unbye - (in reply to uses's message or with user's numeric id as an argument) unban user in all registered chats
	- /adm - (in reply to user's message) give the user adminsitrator priviligies
		if supplied with key -rm the command retracts user's adminsitrator priviligies
	- /reg- adds this chat into bot's DB
		if supplied with key -rm the command removes this chat from bot's DB"""
	bot.send_message(
		msg.chat.id,
		help_text
		)

bot.polling(none_stop = True)