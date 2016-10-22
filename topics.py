# -*- coding: utf-8 -*-
import constants
import db
import json
import telegram
import answers
import functions
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ConversationHandler

def insert_topic(bot, update):
    message = update.message.text
    if (message == 'استارتاپ' or message == 'پلتفرم' or message == 'متفرقه' or message == 'چجو'):
        db.insert_topic_to_temp(update.message.chat_id, message)
    else:
        bot.sendMessage(update.message.chat_id,
                        text = 'لطفا از موارد زیر انتخاب کن یا /skip رو بزن',
                        reply_markup = constants.KEYBOARD_TOPIC)
        return constants.STATE_TOPIC
    bot.sendMessage(update.message.chat_id,
                    text ='برای ارسال سوال /done رو بزن و در صورت منصرف شدن /skip رو بزن' ,
                    reply_markup = constants.KEYBOARD_ANSWER_INSERT)
    return constants.STATE_TOPIC

def select_topics(bot, chat_id, callback = False, m_id = 0):
    text = 'موضوع هایی که میخوای توی اونا واست سوال ارسال بشه رو انتخاب کن'
    topics = db.get_user_topics(chat_id)
    p_number = functions.enToPersianNumb(db.topic_follower_number('پلتفرم'))
    s_number = functions.enToPersianNumb(db.topic_follower_number('استارتاپ'))
    c_number = functions.enToPersianNumb(db.topic_follower_number('چجو'))
    o_number = functions.enToPersianNumb(db.topic_follower_number('متفرقه'))
    if 'پلتفرم' in topics:
        platform_text = '🌕 پلتفرم'
    else:
        platform_text = '⚪️ پلتفرم'
    if 'استارتاپ' in topics:
        startup_text = '🌕 استارتاپ'
    else:
        startup_text = '⚪️ استارتاپ'
    if 'متفرقه' in topics:
        other_text = '🌕 متفرقه'
    else:
        other_text = '⚪️ متفرقه'
    if 'چجو' in topics:
        chejoo_text = '🌕 چجو'
    else:
        chejoo_text = '⚪️ چجو'
    buttons = [
        [InlineKeyboardButton(text=platform_text+' '+p_number,callback_data='followTopic_پلتفرم'),
         InlineKeyboardButton(text=startup_text+' '+s_number,callback_data='followTopic_استارتاپ')],
        [InlineKeyboardButton(text=other_text+ ' '+o_number,callback_data='followTopic_متفرقه'),
         InlineKeyboardButton(text=chejoo_text+' '+c_number,callback_data='followTopic_چجو')]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if callback:
        bot.editMessageReplyMarkup(chat_id = chat_id, message_id = m_id, reply_markup = keyboard)
    else:
        bot.sendMessage(chat_id = chat_id, text = text, reply_markup = keyboard)
