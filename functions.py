
# -*- coding: utf-8 -*-
from telegram import ForceReply
from telegram.ext import ConversationHandler
import telegram
import constants
import answers
import db
import questions
import users
import comments
import topics
import re

def call_handler(bot, update):
    query = update.callback_query
    splited_query = query.data.split("_")

    # print(query.id)
    if db.user_is_blocked(query.from_user.id):
        if db.user_is_admin(query.from_user.id):
            pass
        else:
            bot.answerCallbackQuery(query.id, text='متاسفم شما بلاک شده اید و نمیتوانید از این بات استفاده کنید 😶', show_alert=True)
            return constants.STATE_MAIN

    if (splited_query[0] == 'answer'):
        if (db.get_question(splited_query[1]) == None ):
            bot.answerCallbackQuery(query.id,
                                    text='سوال حذف شده است')
            # bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        db.unactivate(query.from_user.id)
        bot.sendMessage(chat_id=query.from_user.id,text=constants.TEXT_BREAKE)
        questions.show_question(splited_query[1], query.from_user.id, bot, True)
        bot.sendMessage(chat_id=query.from_user.id,text="جواب خود را وارد کنید یا اگر منصرف شده اید /skip را بزنید ", reply_markup=constants.KEYBOARD_ANSWER_CANCEL)
        db.insert_answer_to_temp(query.from_user.id, splited_query[1])
        bot.answerCallbackQuery(query.id, text='میتوانید جواب خود را وارد کنید')
        return constants.STATE_ANSWER_INSERT

    elif (splited_query[0] == 'edit'):
        if (db.get_question(splited_query[1]) == None ):
            bot.answerCallbackQuery(query.id,
                                    text='سوال حذف شده است')
            # bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        db.unactivate(query.from_user.id)
        bot.sendMessage(chat_id=query.from_user.id,text=constants.TEXT_BREAKE)
        questions.show_question(splited_query[1], query.from_user.id, bot, True)
        last_answer = db.get_answer(splited_query[1]+'-'+splited_query[2])['text']
        bot.sendMessage(chat_id=query.from_user.id,text="جواب قبلی شما:\n"+last_answer)
        bot.sendMessage(chat_id=query.from_user.id,text="جواب جدید خود را وارد کنید یا اگر منصرف شده اید /skip را بزنید ", reply_markup = constants.KEYBOARD_ANSWER_CANCEL)
        db.insert_answer_to_temp_edit(query.from_user.id, splited_query[1])
        bot.answerCallbackQuery(query.id, text='اکنون میتوانید جواب قبلی خود را ویرایش کنید')
        return constants.STATE_ANSWER_EDIT

    elif (splited_query[0] == 'likequestion'):
        if (db.get_question(splited_query[1]) == None ):
            bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        q_id = splited_query[1]
        fo_or_unfo = db.follow_or_unfollow_question(q_id, query.from_user.id)
        questions.show_question(splited_query[1],
                                query.from_user.id,
                                bot,
                                withans = False,
                                callback = True,
                                msg_id = query.message.message_id)

        for m in db.get_msgid_and_user_of_question(q_id):
            user_id = m['u_id']
            msg_id = m['msg_id']
            try:
                questions.show_question(q_id,
                                        user_id,
                                        bot,
                                        withans = False,
                                        callback = True,
                                        msg_id = msg_id)
            except:
                pass

        if fo_or_unfo:
            bot.answerCallbackQuery(query.id, text='سوال را دنبال کردی')
        else:
            bot.answerCallbackQuery(query.id, text='دیگر سوال را دنبال نمیکنی')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'nextanswer'):
        answers.show_answers(bot,
                             query.from_user.id,
                             splited_query[1],
                             int(splited_query[2]),
                             msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='جواب بعد نمایش داده شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'beforanswer'):
        answers.show_answers(bot,
                             query.from_user.id,
                             splited_query[1],
                             int(splited_query[2]),
                             msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='جواب قبل نمایش داده شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'upvote'):
        ann_id = splited_query[2]
        upvot = db.upvote_answer(ann_id,
                                 query.from_user.id)
        answers.show_answers(bot,
                             query.from_user.id,
                             splited_query[1],
                             i = int(splited_query[3]),
                             msg_id = query.message.message_id,
                             up_or_down = True)
        bot.answerCallbackQuery(query.id, text='درخواست شما انجام شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'downvote'):
        ann_id = splited_query[2]
        upvot = db.downvote_answer(ann_id,
                                 query.from_user.id)
        answers.show_answers(bot,
                             query.from_user.id,
                             splited_query[1],
                             i = int(splited_query[3]),
                             msg_id = query.message.message_id,
                             up_or_down = True)
        bot.answerCallbackQuery(query.id, text='درخواست شما انجام شد')
        return constants.STATE_MAIN

#upvote and downvote answers in reply
    elif (splited_query[0] == 'up'):
        ann_id = splited_query[2]
        upvot = db.upvote_answer(ann_id,
                                 query.from_user.id)
        # answers.show_answer(bot,
        #                     query.from_user.id,
        #                     splited_query[1],
        #                     ann_id,
        #                     msg_id = query.message.message_id)

        for message in db.get_msgid_and_user_of_answer(ann_id):
            try:
                answers.show_answer(bot,
                                    message['u_id'],
                                    splited_query[1],
                                    ann_id,
                                    msg_id = message['msg_id'])
            except:
                pass

        bot.answerCallbackQuery(query.id, text='درخواست شما انجام شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'down'):
        ann_id = splited_query[2]
        upvot = db.downvote_answer(ann_id,
                                 query.from_user.id)
        # answers.show_answer(bot,
        #                      query.from_user.id,
        #                      splited_query[1],
        #                      ann_id,
        #                      msg_id = query.message.message_id)
        for message in db.get_msgid_and_user_of_answer(ann_id):
            try:
                answers.show_answer(bot,
                                    message['u_id'],
                                    splited_query[1],
                                    ann_id,
                                    msg_id = message['msg_id'])
            except:
                pass
        bot.answerCallbackQuery(query.id, text='درخواست شما انجام شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'deleteQuestion'):
        db.delete_question(splited_query[1])
        bot.answerCallbackQuery(query.id ,
                                text="سوال با موفقیت حذف شد")

    elif (splited_query[0] == 'nextpage'):
        ii = int(splited_query[1])
        questions.show_last_questions(bot,
                                      query.from_user.id,
                                      ii,
                                      number = 5,
                                      callback = True,
                                      m_id = query.message.message_id,
                                      topic = splited_query[2])
        bot.answerCallbackQuery(query.id, text='صفحه بعد لود شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'beforpage'):
        ii = int(splited_query[1])
        questions.show_last_questions(bot,
                                      query.from_user.id,
                                      ii,
                                      number = 5,
                                      callback = True,
                                      m_id = query.message.message_id,
                                      topic = splited_query[2])
        bot.answerCallbackQuery(query.id, text='صفحه قبل لود شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'nextpageuserquestions'):
        ii = int(splited_query[1])
        user_id = int(splited_query[2])
        questions.show_questions_asked_by_user(bot,
                                               query.from_user.id,
                                               user_id,
                                               ii,
                                               limit = 5,
                                               callback = True,
                                               m_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='صفحه بعد لود شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'beforepageuserquestions'):
        ii = int(splited_query[1])
        user_id = int(splited_query[2])
        questions.show_questions_asked_by_user(bot,
                                               query.from_user.id,
                                               user_id,
                                               ii,
                                               limit = 5,
                                               callback = True,
                                               m_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='صفحه قبل لود شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'followUser'):
        u_id = int(splited_query[1])
        fo_or_unfo = db.follow_or_unfollow_user(u_id, query.from_user.id)
        users.show_user(bot, query.from_user.id, u_id,
                        callback = True, msg_id = query.message.message_id)
        if fo_or_unfo:
            bot.answerCallbackQuery(query.id, text='کاربر را دنبال کردی')
        else:
            bot.answerCallbackQuery(query.id, text='دیگر کاربر را دنبال نمیکنی')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'notavailable0'):
        bot.answerCallbackQuery(query.id,text='بعدی وجود ندارد 😁')

    elif (splited_query[0] == 'notavailable1'):
        bot.answerCallbackQuery(query.id,text='قبلتر از این موجود نیست 😁')

    elif (splited_query[0] == 'comments'):
        db.unactivate(query.from_user.id)
        an_id = splited_query[1]
        q_id = splited_query[3]
        u_id = query.from_user.id
        bot.sendMessage(chat_id=query.from_user.id,text=constants.TEXT_BREAKE)
        answers.show_answer(bot, u_id, q_id, an_id, True)
        if int(splited_query[2]) > 0:
            comments.show_comments(bot, u_id, an_id)
        db.insert_comment_to_temp(u_id, an_id)
        bot.sendMessage(query.from_user.id,
                        text ='اگر تمایل داری کامنت خودت را وارد کن وگرنه /skip رو بزن',
                        reply_markup = constants.KEYBOARD_ANSWER_CANCEL)
        bot.answerCallbackQuery(query.id, text='کامنتها لوود شدند اگر تمایل داری کامنت خودت را وارد کن')
        return constants.STATE_COMMENT

    elif (splited_query[0] == 'followTopic'):
        fo_or_unfo = db.follow_or_unfollow_topic(query.from_user.id, splited_query[1])
        topics.select_topics(bot, query.from_user.id, True, m_id=query.message.message_id)
        if fo_or_unfo:
            bot.answerCallbackQuery(query.id, text='موضوع {} به علاقه مندی های شما اضافه شد'.format(splited_query[1]))
        else:
            bot.answerCallbackQuery(query.id, text='موضوع {} از علاقه مندی های شما حذف گردید'.format(splited_query[1]))

    elif (splited_query[0] == 'nextuser'):
        users.show_top_users(bot, query.from_user.id, i = int(splited_query[1]), callback = True, msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='کاربر بعد نمایش داده شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'beforuser'):
        users.show_top_users(bot, query.from_user.id, i = int(splited_query[1]), callback = True, msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='کاربر قبل نمایش داده شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'followUserintop'):
        u_id = int(splited_query[1])
        fo_or_unfo = db.follow_or_unfollow_user(u_id, query.from_user.id)
        users.show_top_users(bot, query.from_user.id, i = int(splited_query[2]),
                        callback = True, msg_id = query.message.message_id)
        if fo_or_unfo:
            bot.answerCallbackQuery(query.id, text='کاربر را دنبال کردی')
        else:
            bot.answerCallbackQuery(query.id, text='دیگر کاربر را دنبال نمیکنی')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'blockorunblock'):
        u_id = int(splited_query[1])
        if db.user_is_blocked(u_id):
            db.unblock_user(u_id)
            bot.answerCallbackQuery(query.id, text='کاربر آنبلاک شد')
        else:
            db.block_user(u_id)
            db.unactivate(u_id)
            bot.answerCallbackQuery(query.id, text='کاربر بلاک شد')

    elif (splited_query[0] == 'upinuseranswers'):
        ann_id = splited_query[1]
        user_id = int(splited_query[2])
        number = int(splited_query[3])
        upvot = db.upvote_answer(ann_id,
                                 query.from_user.id)
        answers.show_answers_of_user(bot,
                                     query.from_user.id,
                                     user_id,
                                     i = number,
                                     show = False,
                                     msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='درخواست شما انجام شد')
        return constants.STATE_MAIN


    elif (splited_query[0] == 'downinuseranswers'):
        ann_id = splited_query[1]
        user_id = int(splited_query[2])
        number = int(splited_query[3])
        upvot = db.downvote_answer(ann_id,
                                   query.from_user.id)
        answers.show_answers_of_user(bot,
                                     query.from_user.id,
                                     user_id,
                                     i = number,
                                     show = False,
                                     msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='درخواست شما انجام شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'nextanswerofuser'):
        user_id = int(splited_query[1])
        number = int(splited_query[2])
        answers.show_answers_of_user(bot,
                                     query.from_user.id,
                                     user_id,
                                     i = number,
                                     show = False,
                                     msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='جواب بعدی نمایش داده شد')
        return constants.STATE_MAIN

    elif (splited_query[0] == 'beforanswerofuser'):
        user_id = int(splited_query[1])
        number = int(splited_query[2])
        answers.show_answers_of_user(bot,
                                     query.from_user.id,
                                     user_id,
                                     i = number,
                                     show = False,
                                     msg_id = query.message.message_id)
        bot.answerCallbackQuery(query.id, text='جواب قبل نمایش داده شد')
        return constants.STATE_MAIN

    else:
        return constants.STATE_MAIN

def enToPersianNumb(number):
    dic = {
        '0':'۰',
        '1':'۱',
        '2':'۲',
        '3':'۳',
        '4':'۴',
        '5':'۵',
        '6':'۶',
        '7':'۷',
        '8':'۸',
        '9':'۹',
        '.':'.',
    }
    return multiple_replace(dic, number)

def multiple_replace(dic, text):
    pattern = "|".join(map(re.escape, dic.keys()))
    return re.sub(pattern, lambda m: dic[m.group()], str(text))
