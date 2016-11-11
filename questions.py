# -*- coding: utf-8 -*-
import constants
import db
import json
import telegram
import answers
import functions
from khayyam import JalaliDate
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ConversationHandler
from random import randint

def show_question(q_id, chat_id, bot, withans = False, callback = False, msg_id = 0):
    q = db.get_question(q_id)
    if (q == None):
        return -1
    question = q["question"]
    q_link = '/q'+str(q['msg_id'])
    asker_id = q["user_id"]
    q_date = str(q['date'].date())
    date = JalaliDate.strptime(q_date, '%Y-%m-%d')
    datestr = functions.enToPersianNumb(date.strftime('%Y/%m/%d'))
    asker = db.get_user(asker_id)
    topic = q['topics'][0]
    like = len(q['followers'])
    if chat_id in q['followers']:
        text_like = 'شما و '+functions.enToPersianNumb(like-1)+' نفر ♥️'
    else:
        text_like =functions.enToPersianNumb(like) + ' نفر♥️ '
    if (asker['username'] == '') or not asker['show_username']:
        asker = '/u'+str(asker_id)
    else:
        asker = '/u'+asker['username']
    # asker = '/u'+str(asker_id)
    if db.user_have_answered(q_id, chat_id):
        answer_text = 'ویرایش جواب'
        answer_callback_data = 'edit_'+str(q_id)+"_"+str(chat_id)
    else:
        answer_text ='📝جواب میدم'
        answer_callback_data = 'answer_'+str(q_id)+'_'+str(chat_id)
    if db.user_is_admin(chat_id):
        delete_text = 'حذف'
    else:
        delete_text = ''
    buttons = [[
        InlineKeyboardButton(text=answer_text,\
                             callback_data=answer_callback_data),
        InlineKeyboardButton(text=text_like,
                             callback_data='likequestion_'+str(q_id))],
               [InlineKeyboardButton(text=delete_text,
                                     callback_data='deleteQuestion_'+ str(q_id))
         ]]
    keyboard = InlineKeyboardMarkup(buttons)
    text_message = 'سوال در موضوع {} '.format(topic)+constants.TEXT_QUESTION+'\n'+'🤔 سوال\n   '+question+'؟\n' + '\n لینک سوال: '+ q_link + '\n\nAsked by '+asker+'\n'+datestr
    if withans:
        bot.sendMessage(chat_id, text = text_message)
    else:
        if (callback == False):
            msg = bot.sendMessage(chat_id, text = text_message,
                                  reply_markup = keyboard)
            db.add_msgid_and_user_to_recent_messages_question(chat_id, q_id, msg['message_id'])
            if db.have_answer(q_id):
                answers.show_answers(bot, chat_id, q_id,show=True)
        else:
            bot.editMessageReplyMarkup(chat_id = chat_id,
                                       message_id = msg_id ,
                                       reply_markup = keyboard)

    # ForceReply

def insert_question(bot, update):
    msg = update.message
    if msg.text == 'سوالای اخیر' or msg.text == '🤔 از چجو بپرس' or msg.text == '⚙ تنظیمات' or msg.text == '👤 پروفایل ' or msg.text == 'لیست کاربران':
        return constants.STATE_ASK
    question_id = str(msg.message_id)+'-'+str(msg.chat_id)
    db.insert_question_to_temp(msg.message_id, msg.text, msg.chat_id, msg.date)
    # db.insert_new_question(msg.message_id, msg.text, msg.chat_id, msg.date)
    bot.sendMessage(update.message.chat_id,
                    text = "لطفا موضوع سوال خود را از موارد زیر انتخاب کنید یا اگر منصرف شده اید /skip را بزنید  😎",
                    reply_markup = constants.KEYBOARD_TOPIC)
    # bot.sendMessage(update.message.chat_id,
                    # text = " سوالت با موفقیت ثبت شد",
                    # reply_markup = constants.KEYBOARD_MAIN)
    return constants.STATE_TOPIC

def finish_question(bot, update):
    u_id = update.message.chat_id
    q_id = db.push_question_from_temp_to_questions(u_id)
    # db.follow_or_unfollow_question(q_id, u_id)
    bot.sendMessage(chat_id = u_id, text='سوالت با موفقیت ثبت شد 🤓', reply_markup= constants.KEYBOARD_MAIN)
    db.activate(update.message.chat_id)
    show_question_to_all_topic_followers(q_id, bot)
    return constants.STATE_MAIN

def skip_question(bot, update):
    bot.sendMessage(update.message.chat_id,\
                    text ="سوالی ثبت نشد ☹️", reply_markup= constants.KEYBOARD_MAIN)
    db.empty_temp(update.message.chat_id)
    db.activate(update.message.chat_id)
    return constants.STATE_MAIN

def show_random_question(bot, user_id):
    ques = db.get_last_10_questions()
    i = randint(0, len(ques)-1)
    show_question(ques[i]['id'], user_id, bot)

def show_question_to_followers(qid, anid, bot, user_id):
    followers = db.get_followers_question(qid)
    # user_followers = db.get_followers_user(user_id)
    topic = db.get_topic_of_question(qid)
    followers = db.get_users_followed_topic(topic)
    for user in followers:
        user = user['id']
        if db.user_is_active(user):
            try:
                # bot.sendMessage(user, text='سوالی که قبلا لایک کرده بودید جواب داده شد 😍')
                bot.sendMessage(user, text='به سوال زیر که در موضوع {} پرسیده شده بود جوابی جدید داده شد 😍'.format(topic))
                answers.show_answer(bot, user, qid, anid, True)
            except:
                print('exeption')
                db.unactivate(user)

    # for user in user_followers :
    #     if db.user_is_active(user):
    #         try:
    #             bot.sendMessage(user, text='سوالی که قبلا لایک کرده بودید جواب داده شد 😍')
    #             # show_question(qid, user, bot, withans = True)
    #             answers.show_answer(bot, user, qid, anid, True)
    #         except:
    #             print('exeption')
    #             db.unactivate(user)

def show_question_to_all_topic_followers(qid, bot):
    topic = db.get_topic_of_question(qid)
    all = db.get_users_followed_topic(topic)
    for user in all:
        try:
            bot.sendMessage(user['id'], text='سوال جدید زیر در موضوع {} پرسیده شده 🤓'.format(topic))
            print('yes')
            show_question(qid, user['id'], bot, False)
        except:
            print('except')
            db.unactivate(user['id'])

def show_last_questions(bot, chat_id, i=0 , number=5, callback = False, m_id = 0, topic = 'همه'):
    skip = number * i
    questions = db.get_last_questions(number, skip, topic)
    if (len(questions) < number ):
        next_text ='صفحه بعد'
        next_call ='notavailable0'
    else:
        next_text ='صفحه بعد'
        next_call ='nextpage'+'_'+str(i+1)+'_'+topic
    if (i == 0):
        before_text = 'صفحه قبل'
        before_call ='notavailable1'
    else:
        before_text = 'صفحه قبل'
        before_call = 'beforpage'+'_'+str(i-1)+'_'+topic

    last_questions_text = functions.enToPersianNumb(skip+1)+' تا '+functions.enToPersianNumb(skip+number)+'  سوال اخیر در موضوع {}:\n'.format(topic)
    buttons = [[
        InlineKeyboardButton(text=next_text,
                             callback_data=next_call),
        InlineKeyboardButton(text=before_text,
                             callback_data= before_call)
         ]]
    keyboard = InlineKeyboardMarkup(buttons)

    for q in questions:
        if q['answers'] == None:
            q_number = 0
        else:
            q_number = len(q['answers'])
        q_index = (i*number)+1+questions.index(q)
        text = '\n'+functions.enToPersianNumb(q_index)+' 🤔سوال: '+ q['question']+'؟\nلینک: /q'+str(q['msg_id'])+'\n♥️تعداد دنبال کنندگان : '+ functions.enToPersianNumb(len(q['followers'])) +'\n📝تعداد جواب ها: '+ functions.enToPersianNumb(q_number)+'\n.'
        last_questions_text += text

    if callback:
        bot.editMessageText(chat_id = chat_id, message_id = m_id , text = last_questions_text, reply_markup = keyboard)
    else:
        # bot.sendMessage(chat_id, text = last_questions_text)
        bot.sendMessage(chat_id, text = last_questions_text, reply_markup = keyboard)

def show(bot, update):
    message = update.message.text
    if (message == 'همه'):
        bot.sendMessage(update.message.chat_id, text='سوال های اخیر در همه موضوعها:\n.', reply_markup = constants.KEYBOARD_MAIN)
        bot.sendChatAction(update.message.chat_id, action = 'typing')
        show_last_questions(bot,update.message.chat_id)
        db.activate(update.message.chat_id)
        return constants.STATE_MAIN

    elif (message == 'پلتفرم' or message == 'استارتاپ' or message == 'متفرقه' or message == 'چجو'):
        bot.sendMessage(update.message.chat_id, text='سوال هایی که در موضوع {} مطرح شده:'.format(message), reply_markup = constants.KEYBOARD_MAIN)
        bot.sendChatAction(update.message.chat_id, action = 'typing')
        show_last_questions(bot,update.message.chat_id, topic = message)
        db.activate(update.message.chat_id)
        return constants.STATE_MAIN

    elif (message == '⬅️'):
        bot.sendMessage(update.message.chat_id, text='برگشتی به منوی اصلی 😃', reply_markup = constants.KEYBOARD_MAIN)
        db.activate(update.message.chat_id)
        return constants.STATE_MAIN
    else:
        bot.sendMessage(update.message.chat_id, text='لطفا از منوی زیر انتخاب کنید 😆', reply_markup = constants.KEYBOARD_READ)

def show_questions_asked_by_user(bot, chat_id, u_id, i=0, limit=5, callback = False, m_id = 0):
    skip = i * limit
    questions = db.get_questions_of_user(u_id, skip, limit)
    if (len(questions) < limit ):
        next_text ='صفحه بعد'
        next_call ='notavailable0'
    else:
        next_text ='صفحه بعد'
        next_call ='nextpageuserquestions'+'_'+str(i+1)+'_'+str(u_id)
    if (i == 0):
        before_text = 'صفحه قبل'
        before_call ='notavailable1'
    else:
        before_text = 'صفحه قبل'
        before_call = 'beforepageuserquestions'+'_'+str(i-1)+'_'+str(u_id)
    user_name = db.get_user(u_id)['first_name']
    last_questions_text = functions.enToPersianNumb(skip+1)+' تا '+functions.enToPersianNumb(skip+limit)+'  سوال اخیر {}:\n'.format(user_name)
    buttons = [[
        InlineKeyboardButton(text=next_text,
                             callback_data=next_call),
        InlineKeyboardButton(text=before_text,
                             callback_data= before_call)
         ]]
    keyboard = InlineKeyboardMarkup(buttons)
    for q in questions:
        if q['answers'] == None:
            q_number = 0
        else:
            q_number = len(q['answers'])
        number = (i*limit)+1+questions.index(q)
        text = '\n'+ functions.enToPersianNumb(number)+' 🤔سوال: '+ q['question']+'؟\nلینک: /q'+str(q['msg_id'])+'\n♥️تعداد دنبال کنندگان : '+ functions.enToPersianNumb(len(q['followers'])) +'\n📝تعداد جواب ها: '+ functions.enToPersianNumb(q_number)+'\n.'
        last_questions_text += text

    if callback:
        bot.editMessageText(chat_id = chat_id, message_id = m_id , text = last_questions_text, reply_markup = keyboard)
    else:
        # bot.sendMessage(chat_id, text = last_questions_text)
        bot.sendMessage(chat_id, text = last_questions_text, reply_markup = keyboard)
