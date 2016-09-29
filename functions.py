
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

def call_handler(bot, update):
    query = update.callback_query
    splited_query = query.data.split("_")
    print(query)

    if (splited_query[0] == 'answer'):
        if (db.get_question(splited_query[1]) == None ):
            bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        db.unactivate(query.from_user.id)
        bot.sendMessage(chat_id=query.from_user.id,text=constants.TEXT_BREAKE)
        questions.show_question(splited_query[1], query.from_user.id, bot, True)
        bot.sendMessage(chat_id=query.from_user.id,text="جواب خود را وارد کنید یا اگر منصرف شده اید /skip را بزنید ", reply_markup=constants.KEYBOARD_ANSWER_CANCEL)
        db.insert_answer_to_temp(query.from_user.id, splited_query[1])
        return constants.STATE_ANSWER_INSERT

    elif (splited_query[0] == 'edit'):
        if (db.get_question(splited_query[1]) == None ):
            bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        db.unactivate(query.from_user.id)
        bot.sendMessage(chat_id=query.from_user.id,text=constants.TEXT_BREAKE)
        questions.show_question(splited_query[1], query.from_user.id, bot, True)
        last_answer = db.get_answer(splited_query[1]+'-'+splited_query[2])['text']
        bot.sendMessage(chat_id=query.from_user.id,text="جواب قبلی شما:\n"+last_answer)
        bot.sendMessage(chat_id=query.from_user.id,text="جواب جدید خود را وارد کنید یا اگر منصرف شده اید /skip را بزنید ", reply_markup = constants.KEYBOARD_ANSWER_CANCEL)
        db.insert_answer_to_temp_edit(query.from_user.id, splited_query[1])
        return constants.STATE_ANSWER_EDIT

    elif (splited_query[0] == 'likequestion'):
        if (db.get_question(splited_query[1]) == None ):
            bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        q_id = splited_query[1]
        db.follow_or_unfollow_question(q_id, query.from_user.id)
        questions.show_question(splited_query[1],
                                query.from_user.id,
                                bot,
                                withans = False,
                                callback = True,
                                msg_id = query.message.message_id)
        return constants.STATE_MAIN

    elif (splited_query[0] == 'nextanswer'):
        answers.show_answers(bot,
                             query.from_user.id,
                             splited_query[1],
                             int(splited_query[2]),
                             msg_id = query.message.message_id)
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
        return constants.STATE_MAIN

#upvote and downvote answers in reply
    elif (splited_query[0] == 'up'):
        ann_id = splited_query[2]
        upvot = db.upvote_answer(ann_id,
                                 query.from_user.id)
        answers.show_answer(bot,
                            query.from_user.id,
                            splited_query[1],
                            ann_id,
                            msg_id = query.message.message_id)
        return constants.STATE_MAIN

    elif (splited_query[0] == 'down'):
        ann_id = splited_query[2]
        upvot = db.downvote_answer(ann_id,
                                 query.from_user.id)
        answers.show_answer(bot,
                             query.from_user.id,
                             splited_query[1],
                             ann_id,
                             msg_id = query.message.message_id)
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
                                      callback = True,
                                      m_id = query.message.message_id)
        return constants.STATE_MAIN
    elif (splited_query[0] == 'followUser'):
        u_id = int(splited_query[1])
        db.follow_or_unfollow_user(u_id, query.from_user.id)
        users.show_user(bot, query.from_user.id, u_id,
                        callback = True, msg_id = query.message.message_id)
        return constants.STATE_MAIN
    elif (splited_query[0] == 'notavailable'):
        bot.answerCallbackQuery(query.id,
                                text='انتهای صفحه')
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
                        text ='اگر تمایل داری کامنت خودت رو وارد کن وگرنه /skip رو بزن',
                        reply_markup = constants.KEYBOARD_ANSWER_CANCEL)
        return constants.STATE_COMMENT

    else:
        return constants.STATE_MAIN
