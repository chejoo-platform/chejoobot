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
DATABASE_TABLES = ['USERS', 'QUESTIONS', 'ANSWERS', 'TOPICS', 'TEMP', 'ADMINS']
STATE_MAIN = 0
STATE_ASK = 1
STATE_ANSWER_INSERT = 2
STATE_ANSWER_EDIT = 3

KEYBOARD_MAIN = ReplyKeyboardMarkup([
    [KeyboardButton(text='🤔 از چجو بپرس'),KeyboardButton(text='سوالای اخیر')]
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
