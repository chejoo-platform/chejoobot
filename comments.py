# -*- coding: utf-8 -*-
import constants
import db
import questions
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import answers

def show_comments(bot, chat_id, ann_id):
    comments = db.get_comments(ann_id)
    text = constants.TEXT_COMMENT+'\nآخرین کامنت ها:'
    for c in comments:
        user = db.get_user(c['u_id'])
        if (user['username'] == ''):
            commenter = '/u'+ str(user['id'])
        else:
            commenter = '/u'+user['username']
        text += '\n\n🖇'+c['text']+'\nfrom '+ commenter
    bot.sendMessage(chat_id, text = text)

def insert_comment(bot, update):
    my_comment = update.message.text
    if my_comment == 'سوالای اخیر' or my_comment == '🤔 از چجو بپرس':
        return constants.STATE_COMMENT
    u_id = update.message.chat_id
    ann_id, comment_id = db.insert_comment(u_id, my_comment)
    q = ann_id.split('-')
    q_id = q[0]+'-'+q[1]
    writer_id = int(q[2])
    bot.sendMessage(chat_id=u_id,\
                    text='کامنت شما با موفقیت ثبت شد',
                    reply_markup = constants.KEYBOARD_MAIN)
    db.activate(update.message.chat_id)
    comment = db.get_comment(comment_id)
    show_comment_to_upvoters(bot, comment_id, q_id, writer_id)
    return constants.STATE_MAIN

def cancel_comment(bot, update):
    u_id = update.message.chat_id
    an_id = db.del_comment_from_temp(u_id)
    bot.sendMessage(chat_id = u_id,\
                    text = 'کامنتی ثبت نشد',
                    reply_markup=constants.KEYBOARD_MAIN)
    db.activate(update.message.chat_id)
    return constants.STATE_MAIN

def show_comment_to_upvoters(bot, c_id, q_id, u_id):
    comment = db.get_comment(c_id)
    an_id = comment['an_id']
    question = db.get_question(q_id)
    q_text = question['question']
    q_link = '/q'+ str(question['msg_id'])
    answer = db.get_answer(an_id)['text']
    comment_text = comment['text']
    commenter = comment['u_id']
    username = db.get_user(commenter)['username']
    for user in db.get_answer_upvoters(an_id):
        try:
            bot.sendMessage(user, text= 'برای جوابی که لایک کرده بودید کامنتی جدید گذاشته شده\n'+constants.TEXT_QUESTION+'\n 🤔سوال: \n'+ q_text +'\n لینک سوال:'+ q_link +'\n'+constants.TEXT_ANSWER+'\n📝جواب:'+answer+'\n'+constants.TEXT_COMMENT+'\n🖇کامنت جدید:\n' +comment_text+'\nfrom @'+username)
        except:
            print('user_has_stopped_the_bot')

