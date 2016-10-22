# -*- coding: utf-8 -*-
import constants
import db
import functions
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def show_user(bot, chat_id, u_id, callback = False, msg_id = 0):
    user = db.get_user(u_id)
    if (user['username'] == ''):
        username = user['first_name']+ ' '+user['last_name']
    else:
        username = '@'+user['username']
    q_numbers = functions.enToPersianNumb(str(user['q_numbers']))
    a_numbers = functions.enToPersianNumb(str(user['a_numbers']))
    followers_number = len(user['followers'])
    if (user['username'] == ''):
        user_questions_link = '/w'+str(u_id)
        user_best_answer_link = '/v'+str(u_id)
    else:
        user_questions_link = '/w'+user['username']
        user_best_answer_link = '/v'+user['username']
    user_info = username + '\nپروفایل '+ user['first_name'] + '\n🤔تعداد سوال:  ' + q_numbers +'\n    لینک سوالها: '+user_questions_link + '\n📝تعداد پاسخ:  '+ a_numbers+'\n    لینک جواب ها: '+ user_best_answer_link+'\n⭐امتیاز:  ' + functions.enToPersianNumb(constants.LEVEL_STAGES[user['level']-1])+' / ' +functions.enToPersianNumb(user['score']) + '\nسطح:  ' + functions.enToPersianNumb(user['level'])+'\n.'
    if chat_id in user['followers']:
        text_like = 'شما و '+functions.enToPersianNumb(followers_number-1)+' نفر ♥️'
    else:
        text_like = functions.enToPersianNumb(followers_number)+ ' نفر ♥️ '
    if db.user_is_admin(chat_id):
        block_text = 'بلاک یا آنبلاک'
    else:
        block_text = ''
    buttons = [[
        InlineKeyboardButton(text=text_like,
                             callback_data='followUser_'+str(u_id))],
        [InlineKeyboardButton(text=block_text,
                             callback_data='blockorunblock_'+str(u_id))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if callback:
        bot.editMessageText(chat_id = chat_id, text = user_info, message_id = msg_id, reply_markup = keyboard )
    else:
        bot.sendMessage(chat_id, text = user_info, reply_markup = keyboard)

def show_top_users(bot, chat_id, i = 0, callback = False, msg_id = 0):
    count = db.get_user_numbers()
    user = db.get_ranked_user(i)
    u_id = user['id']
    if (user['username'] == ''):
        username = user['first_name']+ ' '+user['last_name']
    else:
        username = '@'+user['username']
    q_numbers = functions.enToPersianNumb(user['q_numbers'])
    a_numbers = functions.enToPersianNumb(user['a_numbers'])
    followers_number = len(user['followers'])
    if (user['username'] == ''):
        user_questions_link = '/w'+str(u_id)
        user_best_answer_link = '/v'+str(u_id)
    else:
        user_questions_link = '/w'+user['username']
        user_best_answer_link = '/v'+user['username']
    user_info ='رتبه : '+functions.enToPersianNumb(i+1)+'\n' +username + '\nپروفایل '+ user['first_name'] + '\n🤔تعداد سوال:  ' + q_numbers +'\n    لینک سوالها: '+user_questions_link + '\n📝تعداد پاسخ:  '+ a_numbers+'\n    لینک جواب ها: '+ user_best_answer_link+'\n⭐امتیاز:  ' + functions.enToPersianNumb(user['score']) + '\nسطح:  ' + functions.enToPersianNumb(user['level'])+'\n.'
    if chat_id in user['followers']:
        text_like = 'شما و '+functions.enToPersianNumb(followers_number-1)+' ♥️'
    else:
        text_like = functions.enToPersianNumb(followers_number)+ ' نفر ♥️ '
    next_data = 'nextuser_'+str(i+1)
    befor_data = 'beforuser_'+str(i-1)
    if ((i+1) == count):
        next_data = 'notavailable0'
    if (i == 0):
        befor_data = 'notavailable1'
    buttons = [[
        InlineKeyboardButton(text='بعدی',
                             callback_data=next_data),
        InlineKeyboardButton(text=text_like,
                             callback_data='followUserintop_'+str(u_id)+'_'+str(i)),
        InlineKeyboardButton(text='قبلی',
                             callback_data=befor_data)
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if callback:
        bot.editMessageText(chat_id = chat_id, text = user_info, message_id = msg_id, reply_markup = keyboard )
    else:
        bot.sendMessage(chat_id, text = user_info, reply_markup = keyboard)

