# -*- coding: utf-8 -*-
import constants
import db
import questions
import DateConvertor
import functions
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def show_answers(mybot, u_id, q_id, i=0, show = False, msg_id = 0, up_or_down = False):
    answers = db.get_answers(q_id)
    count = len(answers)
    ans = answers[i]
    # ans_rank = constants.ANSWER_RANK[i]
    an_id = ans['id']
    an_date = str(ans['date'].date()).split('-')
    date = DateConvertor.shamsiDate(int(an_date[0]),int(an_date[1]),int(an_date[2]))
    date = functions.enToPersianNumb(date)
    comments = ans['comments']
    comments_number = len(comments)
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
        writer = '/u'+str(writer_id)
    else:
        writer = '/u'+writer['username']
    if i < 3:
        answer_rank = ['بهترین جواب', 'دومین جواب', 'سومین جواب'][i]
    else:
        answer_rank = functions.enToPersianNumb(i+1)+'اُمین جواب'
    text = answer_rank +'\n'+ constants.TEXT_ANSWER+'\n'+'🖊 جواب'+ ans['text'] + str('\n\nfrom ')+writer+'\n'+str(date)
    next_data = 'nextanswer_'+str(q_id)+'_'+str(i+1)
    next_text = 'جواب بعد'
    befor_data = 'beforanswer_'+str(q_id)+'_'+str(i-1)
    befor_text = 'جواب قبل'
    if ((i+1) == count):
        next_data = 'notavailable0'
        # next_text =''
    if (i == 0):
        befor_data = 'notavailable1'
        # befor_text =''
    buttons = [[
        InlineKeyboardButton(text=next_text,\
                             callback_data=next_data),
        InlineKeyboardButton(text=text_upvote+' '+functions.enToPersianNumb(upvotes),\
                             callback_data='upvote_'+ str(q_id)+'_'+ an_id + '_'+ str(i)),
        InlineKeyboardButton(text=text_downvote+' '+functions.enToPersianNumb(downvotes),\
                             callback_data='downvote_'+ str(q_id)+'_'+ an_id + '_'+ str(i)),
        InlineKeyboardButton(text=befor_text,\
                             callback_data=befor_data)
         ],
    [InlineKeyboardButton(text= 'کامنت '+ functions.enToPersianNumb(comments_number),
                          callback_data='comments_'+an_id+'_'+functions.enToPersianNumb(comments_number)+'_'+q_id)]]
    keyboard = InlineKeyboardMarkup(buttons)
    if show:
        mybot.sendMessage(u_id, text = text, reply_markup = keyboard)
    else:
        if up_or_down:
            mybot.editMessageText(chat_id = u_id, message_id = msg_id, text = text, reply_markup = keyboard)
        else:
            mybot.editMessageText(chat_id = u_id, message_id = msg_id , text = text, reply_markup = keyboard)

def show_answer(mybot, u_id, q_id, an_id, show = False, msg_id = 0):
    question = db.get_question(q_id)
    q_text = question['question']
    q_link = '/q'+ str(question['msg_id'])
    ans = db.get_answer(an_id)
    an_date = str(ans['date'].date()).split('-')
    date = DateConvertor.shamsiDate(int(an_date[0]),int(an_date[1]),int(an_date[2]))
    date = functions.enToPersianNumb(date)
    comments = ans['comments']
    comments_number = len(comments)
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
        writer = '/u'+str(writer_id)
    else:
        writer = '/u'+writer['username']
    text = constants.TEXT_QUESTION+'\n'+'🤔سوال: '+ q_text +'\n لینک: '+ q_link+'\n'+constants.TEXT_ANSWER+'\n✏️جواب : '+ ans['text'] + '\n\nfrom '+writer+ '\n'+ date
    buttons = [[
        InlineKeyboardButton(text=text_upvote+' '+functions.enToPersianNumb(upvotes),\
                             callback_data='up_'+ str(q_id)+'_'+ an_id),
        InlineKeyboardButton(text=text_downvote+' '+functions.enToPersianNumb(downvotes),\
                             callback_data='down_'+ str(q_id)+'_'+ an_id)],
        [InlineKeyboardButton(text= 'کامنت '+ functions.enToPersianNumb(comments_number),
                              callback_data='comments_'+an_id+'_'+functions.enToPersianNumb(comments_number)+ '_'+ q_id)]
         ]
    keyboard = InlineKeyboardMarkup(buttons)
    if show:
        msg = mybot.sendMessage(u_id, text = text, reply_markup = keyboard)
        db.add_msgid_and_user_to_recent_messages_answer(u_id, an_id, msg['message_id'])
    else:
        x = mybot.editMessageReplyMarkup(chat_id = u_id, message_id = msg_id , reply_markup = keyboard)

def show_answers_of_user(mybot, u_id, user_id, i = 0, show = True, msg_id = 0):
# def show_answer(mybot, u_id, q_id, an_id, show = False, msg_id = 0):
    ans = db.get_answer_of_user(user_id, i)
    if ans == False:
        mybot.sendMessage(u_id, text = 'این کاربر تا کنون به سوالی پاسخ نداده', reply_markup = constants.KEYBOARD_MAIN)
        return 0
    an_id = ans['id']
    q_id = ans['q_id']
    question = db.get_question(q_id)
    q_text = question['question']
    q_link = '/q'+ str(question['msg_id'])
    # ans = db.get_answer(an_id)
    an_date = str(ans['date'].date()).split('-')
    date = DateConvertor.shamsiDate(int(an_date[0]),int(an_date[1]),int(an_date[2]))
    date = functions.enToPersianNumb(date)
    comments = ans['comments']
    comments_number = len(comments)
    writer_id = user_id
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
        writer_link = '/u'+str(writer_id)
    else:
        writer_link = '/u'+writer['username']
    text = 'سوال هایی که {} اخیرا جواب داده:\n'.format(writer['first_name']) +'شماره '+functions.enToPersianNumb(i+1)+'\n'+ constants.TEXT_QUESTION+'\n'+'🤔سوال: '+ q_text +'\n لینک: '+ q_link+'\n'+constants.TEXT_ANSWER+'\n✏️جواب : '+ ans['text'] + '\n\nfrom '+writer_link+ '\n'+ date
    text_next = 'بعدی'
    text_befor = 'قبلی'
    if i==0:
        call_befor = 'notavailable1'
    else:
        call_befor = 'beforanswerofuser_'+ str(user_id)+'_'+str(i-1)
    if i+1 == writer['a_numbers']:
        call_next = 'notavailable0'
    else:
        call_next = 'nextanswerofuser_'+ str(user_id)+'_'+str(i+1)
    buttons =[
        [
            InlineKeyboardButton(text=text_next,\
                                 callback_data=call_next),
            InlineKeyboardButton(text=text_upvote+' '+functions.enToPersianNumb(upvotes),\
                                 callback_data='upinuseranswers_'+an_id+'_' + str(user_id)+'_'+str(i)),
            InlineKeyboardButton(text=text_downvote+' '+functions.enToPersianNumb(downvotes),\
                                 callback_data='downinuseranswers_'+an_id+'_'+ str(user_id)+'_'+str(i)),
            InlineKeyboardButton(text=text_befor,\
                             callback_data=call_befor)
        ],
        [
            InlineKeyboardButton(text= 'کامنت '+ functions.enToPersianNumb(comments_number),
                            callback_data='comments_'+an_id+'_'+functions.enToPersianNumb(comments_number)+ '_'+ q_id)
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    if show:
        mybot.sendMessage(u_id, text = text, reply_markup = keyboard)
    else:
        mybot.editMessageText(chat_id = u_id, text = text, message_id = msg_id , reply_markup = keyboard)


def edit_answer(bot, update):
    my_answer = update.message.text
    u_id = update.message.chat_id
    db.update_answer_of_temp(u_id, my_answer)
    bot.sendMessage(chat_id=u_id,\
                    text='اگر جوابتان پایان یافته روی /done بزنید در غیر اینصورت ادامه جوابتان را وارد نمایید اگر از جواب دادن منصرف شده اید میتوانید /skip را بزنید: ',
                    reply_markup = constants.KEYBOARD_ANSWER_INSERT)
    # db.insert_new_answer(q_id, answer)
    db.unactivate(u_id)
    return constants.STATE_ANSWER_EDIT

def insert_answer(bot, update):
    my_answer = update.message.text
    u_id = update.message.chat_id
    db.update_answer_of_temp(u_id, my_answer)
    bot.sendMessage(chat_id=u_id,\
                    text='اگر جوابتان پایان یافته روی /done بزنید😊 در غیر اینصورت ادامه جوابتان را وارد نمایید😚 اگر از جواب دادن منصرف شده اید میتوانید /skip را بزنید😒: ',
                    reply_markup = constants.KEYBOARD_ANSWER_INSERT)
    db.unactivate(u_id)
    return constants.STATE_ANSWER_INSERT

def finish_answer(bot, update):
    u_id = update.message.chat_id
    qid, an_id = db.push_answer_form_temp_to_answers(u_id)
    # db.upvote_answer(an_id, u_id)
    bot.sendMessage(chat_id = u_id, text=' جواب شما با موفقیت ثبت شد 🤗', reply_markup= constants.KEYBOARD_MAIN)
    db.activate(update.message.chat_id)
    # questions.show_question_to_followers(qid, an_id, bot, u_id)
    questions.show_question_to_followers(qid, an_id, bot, u_id)
    return constants.STATE_MAIN

def cancel_answer(bot, update):
    u_id = update.message.chat_id
    qid = db.del_answer_from_temp(u_id)
    bot.sendMessage(chat_id = u_id,\
                    text = 'جوابی ثبت نشد 🙄',
                    reply_markup=constants.KEYBOARD_MAIN)
    questions.show_question(qid, u_id, bot, False)
    db.activate(update.message.chat_id)
    return constants.STATE_MAIN

def finish_edit_answer(bot, update):
    u_id = update.message.chat_id
    qid, anid = db.push_answer_form_temp_to_answers_edit_mod(u_id)
    bot.sendMessage(chat_id = u_id, text=' جواب ادیت شده ی شما با موفقیت ثبت شد 🤗', reply_markup= constants.KEYBOARD_MAIN)
    show_answer(bot, u_id, qid, anid, True)
    db.activate(update.message.chat_id)
    # questions.show_question(qid, u_id, bot)
    return constants.STATE_MAIN

def cancel_edit_answer(bot, update):
    u_id = update.message.chat_id
    qid = db.del_answer_from_temp(u_id)
    bot.sendMessage(chat_id = u_id,\
                    text = 'جواب شما بدون تغییر باقی ماند 😎',
                    reply_markup=constants.KEYBOARD_MAIN)
    questions.show_question(qid, u_id, bot, False)
    db.activate(update.message.chat_id)
    return constants.STATE_MAIN

def show_best_answer_of_user(bot, chat_id, user_id):
    answer = db.get_best_answer_of_this_user(user_id)
    if answer == False:
        bot.sendMessage(chat_id, text='این کاربر تا کنون به سوالی پاسخ نداده')
    else:
        bot.sendMessage(chat_id, text='بهترین جوابی که این کاربر داده جواب زیر میباشد')
        show_answer(bot, chat_id, answer['q_id'], answer['id'], show= True)
