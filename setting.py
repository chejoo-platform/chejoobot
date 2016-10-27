# -*- coding: utf-8 -*-
import constants
import db
import json
import telegram
import answers
import functions
import topics
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ConversationHandler


def setting_handler(bot, update):
    message = update.message.text
    if (message == '⚙ موضوعهای من'):
        # bot.sendMessage(update.message.chat_id, text='')
        topics.select_topics(bot, update.message.chat_id)
        return constants.STATE_SETTING
    elif (message == '⚙ پروفایل من'):
        telegram_profile_show_setting(bot, update.message.chat_id)
        return constants.STATE_SETTING
    elif (message == '⬅️'):
        bot.sendMessage(update.message.chat_id, text='برگشتی به منوی اصلی 😃', reply_markup = constants.KEYBOARD_MAIN)
        db.activate(update.message.chat_id)
        return constants.STATE_MAIN
    else:
        bot.sendMessage(update.message.chat_id, text='لطفا از منوی زیر انتخاب کنید 😆', reply_markup = constants.KEYBOARD_SETTING)

def telegram_profile_show_setting(bot, chat_id, call_back = False, msg_id = 0):
    username_show_stat = db.get_user(chat_id)['show_username']
    text = 'با کلید های زیر نمایش یا عدم نمایش یوزرنیم تلگرام خود در چجو را نتظیم کنید'
    if username_show_stat:
        on_text = '🌕 نمایش بده'
        off_text = '⚪️ نمایش نده'
    else:
        on_text = '⚪️ نمایش بده'
        off_text = '🌕 نمایش نده'
    buttons = [
        [InlineKeyboardButton(text=off_text,callback_data='showusernameoff'),
         InlineKeyboardButton(text=on_text,callback_data='showusernameon')],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if call_back:
        bot.editMessageReplyMarkup(chat_id = chat_id, message_id = msg_id, reply_markup = keyboard)
    else:
        bot.sendMessage(chat_id = chat_id, text = text, reply_markup = keyboard)
