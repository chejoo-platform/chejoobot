
# -*- coding: utf-8 -*-
from telegram import ForceReply
from telegram.ext import ConversationHandler
import telegram
import constants
import answers
import db
import questions
def call_handler(bot, update):
    query = update.callback_query
    splited_query = query.data.split("_")

    if (splited_query[0] == 'answer'):
        if (db.get_question(splited_query[1]) == None ):
            bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        bot.sendMessage(chat_id=query.from_user.id,text="جواب خود را وارد کنید یا اگر منصرف شده اید /skip را بزنید ", reply_markup=constants.KEYBOARD_ANSWER_CANCEL)
        db.insert_answer_to_temp(query.from_user.id, splited_query[1])
        return constants.STATE_ANSWER_INSERT

    elif (splited_query[0] == 'edit'):
        if (db.get_question(splited_query[1]) == None ):
            bot.sendMessage(chat_id=query.from_user.id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
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
                             msg_id = query.message.message_id)
        return constants.STATE_MAIN

    elif (splited_query[0] == 'downvote'):
        ann_id = splited_query[2]
        upvot = db.downvote_answer(ann_id,
                                 query.from_user.id)
        answers.show_answers(bot,
                             query.from_user.id,
                             splited_query[1],
                             i = int(splited_query[3]),
                             msg_id = query.message.message_id)
        return constants.STATE_MAIN

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
        ii = int(splited_query [1])
        print(ii)
        questions.show_last_questions(bot,
                                      query.from_user.id,
                                      ii,
                                      callback = True,
                                      m_id = query.message.message_id)
        return constants.STATE_MAIN
    else:
        return constants.STATE_MAIN
