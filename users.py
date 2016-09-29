# -*- coding: utf-8 -*-
import constants
import db
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def show_user(bot, chat_id, u_id, callback = False, msg_id = 0):
    user = db.get_user(u_id)
    if (user['username'] == ''):
        username = user['first_name']+ ' '+user['last_name']
    else:
        username = '@'+user['username']
    q_numbers = str(user['q_numbers'])
    a_numbers = str(user['a_numbers'])
    followers_number = str(len(user['followers']))
    user_info = username + '\nپروفایل '+ user['first_name'] + '\n🤔تعداد سوال ها :' + q_numbers + '\n📝تعداد پاسخ ها: '+ a_numbers+'\n⭐ستاره: ' + str(user['score']) + '\nمرتبه: ' + constants.USER_LEVELES[user['level']]
    if chat_id in user['followers']:
        text_like = '❤️'
    else:
        text_like = '💔'
    buttons = [[
        InlineKeyboardButton(text=text_like+' '+followers_number,
                             callback_data='followUser_'+str(u_id))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if callback:
        bot.editMessageReplyMarkup(chat_id = chat_id, message_id = msg_id, reply_markup = keyboard )
    else:
        bot.sendMessage(chat_id, text = user_info, reply_markup = keyboard)
