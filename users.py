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
    followers_number = len(user['followers'])
    if (user['username'] == ''):
        user_questions_link = '/w'+str(u_id)
        user_best_answer_link = '/v'+str(u_id)
    else:
        user_questions_link = '/w'+user['username']
        user_best_answer_link = '/v'+user['username']
    user_info = username + '\nپروفایل '+ user['first_name'] + '\n🤔تعداد سوال:  ' + q_numbers +'\n    لینک سوالها: '+user_questions_link + '\n📝تعداد پاسخ:  '+ a_numbers+'\n    لینک بهترین پاسخ: '+ user_best_answer_link+'\n⭐امتیاز:  ' + str(constants.LEVEL_STAGES[user['level']-1])+' / ' +str(user['score']) + '\nسطح:  ' + str(user['level'])+'\n.'
    if chat_id in user['followers']:
        text_like = 'شما + '+str(followers_number-1)+' ♥️'
    else:
        text_like = '♥️ '+str(followers_number)
    buttons = [[
        InlineKeyboardButton(text=text_like,
                             callback_data='followUser_'+str(u_id))
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
    q_numbers = str(user['q_numbers'])
    a_numbers = str(user['a_numbers'])
    followers_number = len(user['followers'])
    if (user['username'] == ''):
        user_questions_link = '/w'+str(u_id)
        user_best_answer_link = '/v'+str(u_id)
    else:
        user_questions_link = '/w'+user['username']
        user_best_answer_link = '/v'+user['username']
    user_info ='رتبه : '+str(i+1)+'\n' +username + '\nپروفایل '+ user['first_name'] + '\n🤔تعداد سوال:  ' + q_numbers +'\n    لینک سوالها: '+user_questions_link + '\n📝تعداد پاسخ:  '+ a_numbers+'\n    لینک بهترین پاسخ: '+ user_best_answer_link+'\n⭐امتیاز:  ' + str(user['score']) + '\nسطح:  ' + str(user['level'])+'\n.'
    if chat_id in user['followers']:
        text_like = 'شما + '+str(followers_number-1)+' ♥️'
    else:
        text_like = '♥️ '+str(followers_number)
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

