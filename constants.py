#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Constants
"""
"""
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from mytoken import TOKEN, DATABASE_DATABASE
# TOKEN = "140381963:AAFZa05H5tmR8TtAUDSdgSxCj8fKsICmFJQ"
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASS = ''
DATABASE_TABLES = ['USERS', 'QUESTIONS', 'ANSWERS', 'TOPICS', 'COMMENTS', 'TEMP', 'ADMINS', 'BLOCKED', 'RECENT_MESSAGES']
USER_LEVELES = ['هیچی', '🐜', '🐞']
LEVEL_STAGES = [10, 20, 30, 50, 80, 130, 210, 340, 560, 910]
STATE_MAIN = 0
STATE_ASK = 1
STATE_ANSWER_INSERT = 2
STATE_ANSWER_EDIT = 3
STATE_COMMENT = 4
STATE_TOPIC = 5
STATE_READ = 6
STATE_UPDATE = 7
TEXT_QUESTION = '❓❓❓❓❓❓❓❓❓'
TEXT_ANSWER = '✏️✏️✏️✏️✏️✏️✏️✏️✏'
TEXT_COMMENT = '📎📎📎📎📎📎📎📎📎'
TEXT_BREAKE = '\n⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️'
HOW_TO_WORK_WITH_BOT = ''
BOT_UPDATE_MESSAGE = '✨✨✨\t✨✨✨\n\nسلام عزیزان با فیدبک های خوب شما ویژگی های جدیدی به چجو اضافه کردیم \nاین ویژگی ها شامل موارد زیر میباشد:\n\n' + '- اضافه شدن موضوع(topic) به سوال ها: \n     با زدن روی تنظیمات میتوانید موضوع هایی که در آنها علاقه مند به دریافت سوال های جدید هستید را انتخاب کنید همچنین در زمان ایجاد سوال یا مشاهده سوال های اخیر میبایست از بین موضوع های موجود انتخاب کنید \n\n- اضافه شدن پروفایل:\n     شما میتوانید پروفایل کاربران را مشاهده کنید و آنها را دنبال کنید تا در صورتی که از طرف ایشان سوالی پرسیده یا جوابی داده شد برای شما ارسال شود \n\n from @chejoo'

ANSWER_RANK = ['بهترین جواب','دومین جواب برتر', 'سومین جواب برتر']
KEYBOARD_MAIN = ReplyKeyboardMarkup([
    [KeyboardButton(text='🤔 از چجو بپرس'),KeyboardButton(text='سوالای اخیر')],
    [KeyboardButton(text='⚙ تنظیمات'), KeyboardButton(text='👤 پروفایل')],
    [KeyboardButton(text = 'لیست کاربران')]
],
                                    resize_keyboard = True)
KEYBOARD_ASK = ReplyKeyboardMarkup([
    [KeyboardButton(text='/skip')]
],
                                   resize_keyboard = True)
KEYBOARD_ANSWER_INSERT = ReplyKeyboardMarkup([
    [KeyboardButton(text='/done'),KeyboardButton(text='/skip')]
],
                                             resize_keyboard =True)
KEYBOARD_ANSWER_CANCEL = ReplyKeyboardMarkup([
    [KeyboardButton(text='/skip')]
],
                                             resize_keyboard= True)
KEYBOARD_TOPIC = ReplyKeyboardMarkup([
    [KeyboardButton(text='پلتفرم'), KeyboardButton(text='استارتاپ')],
    [KeyboardButton(text='متفرقه'), KeyboardButton(text='چجو')],
    [KeyboardButton(text='/skip')]
],
                                   resize_keyboard = True)
KEYBOARD_READ = ReplyKeyboardMarkup([
    [KeyboardButton(text='همه')],
    [KeyboardButton(text='پلتفرم'), KeyboardButton(text='استارتاپ')],
    [KeyboardButton(text='متفرقه'), KeyboardButton(text='چجو')],
    [KeyboardButton(text='⬅️')]
],
                                             resize_keyboard =True)
