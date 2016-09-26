# -*- coding: utf-8 -*-
import constants
import db
import questions
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def show_answers(mybot, u_id, q_id, i=0, show = False, msg_id = 0, up_or_down = False):
    answers = db.get_answers(q_id)
    count = len(answers)
    ans = answers[i]
    an_id = ans['id']
    writer_id = int(ans['id'].split("-")[2])
    upvotes = ans['upvotes']
    downvotes = ans['downvotes']
    if u_id in ans['upvoters']:
        text_upvote ='👍🏻'
        text_downvote = '👎🏿'
    else:
        text_upvote ='👍🏿'
        text_downvote = '👎🏿'
        if u_id in ans['downvoters']:
            text_downvote = '👎🏻'
    writer = db.get_user(writer_id)
    if (writer['username'] == ''):
        writer = writer['first_name']+ ' '+writer['last_name']
    else:
        writer = '@'+writer['username']
    text = '🖊 جواب'+ ans['text'] + str('\n\nfrom ')+writer
    next_data = 'nextanswer_'+str(q_id)+'_'+str(i+1)
    next_text = 'جواب بعد'
    befor_data = 'nextanswer_'+str(q_id)+'_'+str(i-1)
    befor_text = 'جواب قبل'
    if ((i+1) == count):
        next_data = 'notavailable'
        next_text =''
    if (i == 0):
        befor_data = 'notavailable'
        befor_text =''
    buttons = [[
        InlineKeyboardButton(text=befor_text,\
                             callback_data=befor_data),
        InlineKeyboardButton(text=text_upvote+' '+str(upvotes),\
                             callback_data='upvote_'+ str(q_id)+'_'+ an_id + '_'+ str(i)),
        InlineKeyboardButton(text=text_downvote+' '+str(downvotes),\
                             callback_data='downvote_'+ str(q_id)+'_'+ an_id + '_'+ str(i)),
        InlineKeyboardButton(text=next_text,\
                             callback_data=next_data)
         ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if show:
        mybot.sendMessage(u_id, text = text, reply_markup = keyboard)
    else:
        if up_or_down:
            mybot.editMessageReplyMarkup(chat_id = u_id, message_id = msg_id, reply_markup = keyboard)
        else:
            mybot.editMessageText(chat_id = u_id, message_id = msg_id , text = text, reply_markup = keyboard)

def show_answer(mybot, u_id, q_id, an_id, show = False, msg_id = 0):
    question = db.get_question(q_id)
    q_text = question['question']
    q_link = '/q'+ str(question['msg_id'])
    ans = db.get_answer(an_id)
    writer_id = int(an_id.split("-")[2])
    upvotes = ans['upvotes']
    downvotes = ans['downvotes']
    if u_id in ans['upvoters']:
        text_upvote ='👍🏻'
        text_downvote = '👎🏿'
    else:
        text_upvote ='👍🏿'
        text_downvote = '👎🏿'
        if u_id in ans['downvoters']:
            text_downvote = '👎🏻'
    writer = db.get_user(writer_id)
    if (writer['username'] == ''):
        writer = writer['first_name']+ ' '+writer['last_name']
    else:
        writer = '@'+writer['username']
    text = '🤔سوال: '+ q_text +'\n لینک: '+ q_link+'\n\n✏️جواب جدید: '+ ans['text'] + '\n\nfrom '+writer
    buttons = [[
        InlineKeyboardButton(text=text_upvote+' '+str(upvotes),\
                             callback_data='up_'+ str(q_id)+'_'+ an_id),
        InlineKeyboardButton(text=text_downvote+' '+str(downvotes),\
                             callback_data='down_'+ str(q_id)+'_'+ an_id)
         ]]
    keyboard = InlineKeyboardMarkup(buttons)
    if show:
        mybot.sendMessage(u_id, text = text, reply_markup = keyboard)
    else:
        mybot.editMessageReplyMarkup(chat_id = u_id, message_id = msg_id , reply_markup = keyboard)


def edit_answer(bot, update):
    my_answer = update.message.text
    u_id = update.message.chat_id
    db.update_answer_of_temp(u_id, my_answer)
    bot.sendMessage(chat_id=u_id,\
                    text='اگر پاسختان تمام شده روی /done بزنید در غیر اینصورت ادامه جوابتان را وارد نمایید و اگر از جواب دادن منصرف شده اید میتوانید /skip را بزنید: ', reply_markup = constants.KEYBOARD_ANSWER_INSERT)
    # db.insert_new_answer(q_id, answer)
    return constants.STATE_ANSWER_EDIT

def insert_answer(bot, update):
    my_answer = update.message.text
    u_id = update.message.chat_id
    db.update_answer_of_temp(u_id, my_answer)
    bot.sendMessage(chat_id=u_id,\
                    text='اگر پاسختان تمام شده روی /done بزنید در غیر اینصورت ادامه جوابتان را وارد نمایید و اگر از جواب دادن منصرف شده اید میتوانید /skip را بزنید: ', reply_markup = constants.KEYBOARD_ANSWER_INSERT)
    return constants.STATE_ANSWER_INSERT

def finish_answer(bot, update):
    u_id = update.message.chat_id
    qid, an_id = db.push_answer_form_temp_to_answers(u_id)
    bot.sendMessage(chat_id = u_id, text=' جواب شما با موفقیت ثبت شد', reply_markup= constants.KEYBOARD_MAIN)
    questions.show_question_to_followers(qid, an_id, bot)
    return constants.STATE_MAIN

def cancel_answer(bot, update):
    u_id = update.message.chat_id
    qid = db.del_answer_from_temp(u_id)
    bot.sendMessage(chat_id = u_id,\
                    text = 'جوابی ثبت نشد',
                    reply_markup=constants.KEYBOARD_MAIN)
    questions.show_question(qid, u_id, bot, False)
    return constants.STATE_MAIN

def finish_edit_answer(bot, update):
    u_id = update.message.chat_id
    qid, anid = db.push_answer_form_temp_to_answers(u_id)
    bot.sendMessage(chat_id = u_id, text=' جواب ادیت شده ی شما با موفقیت ثبت شد', reply_markup= constants.KEYBOARD_MAIN)
    show_answer(bot, u_id, qid, anid, True)
    # questions.show_question(qid, u_id, bot)
    return constants.STATE_MAIN

def cancel_edit_answer(bot, update):
    u_id = update.message.chat_id
    qid = db.del_answer_from_temp(u_id)
    bot.sendMessage(chat_id = u_id,\
                    text = 'جواب شما بدون تغییر باقی ماند',
                    reply_markup=constants.KEYBOARD_MAIN)
    questions.show_question(qid, u_id, bot, False)
    return constants.STATE_MAIN
