#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import logging
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, NetworkError)
import db
import constants
import questions
import answers
import functions
import users
import comments
import topics

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('chejoobot')

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    from_user = update.message.chat
    if db.check_user(update.message.from_user.id):
        bot.sendMessage(update.message.chat_id,\
                        text ="سلام {} جان قبلا ثبت نام کردی 😜\n.".format(from_user.first_name), reply_markup = constants.KEYBOARD_MAIN)
        db.activate(from_user.id)
    else:
        db.insert_new_user(from_user.id, from_user.first_name, from_user.last_name, from_user.username)
        bot.sendMessage(update.message.chat_id, text =" سلام {} جان خوش اومدی 😍\n.".format(from_user.first_name), reply_markup=constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def registered_user(bot, update):
    from_user = update.message.chat
    if db.check_user(update.message.from_user.id):
        db.activate(from_user.id)
        bot.sendMessage(update.message.chat_id, text = 'لطفا از منوی زیر انتخاب نمایید', reply_markup=constants.KEYBOARD_MAIN)
    else:
        db.insert_new_user(from_user.id, from_user.first_name, from_user.last_name, from_user.username)
        bot.sendMessage(update.message.chat_id, text =" سلام {} جان خوش اومدی 😍\n.".format(from_user.first_name), reply_markup=constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def stop_this_fucking_bot(bot, update):
    return ConversationHandler.END

def main_menue_handler(bot, update):
    message = update.message.text
    if (message == 'سوالای اخیر'):
        bot.sendMessage(update.message.chat_id,
                        text = 'از موضوعات زیر یکی رو انتخاب کن', reply_markup=constants.KEYBOARD_READ)
        db.unactivate(update.message.chat_id)
        return constants.STATE_READ
    elif (message == '🤔 از چجو بپرس'):
        bot.sendMessage(update.message.chat_id,
                        text = ' سوال خودت رو وارد کن یا اگه سوال نداری /skip رو بزن\n.', reply_markup=constants.KEYBOARD_ASK)
        db.unactivate(update.message.chat_id)
        return constants.STATE_ASK
    elif (message == '👤 پروفایل'):
        users.show_user(bot, update.message.chat_id, update.message.chat_id)
        return constants.STATE_MAIN
    elif (message == '⚙ تنظیمات'):
        topics.select_topics(bot, update.message.chat_id)
    else:
        bot.sendMessage(update.message.chat_id, text = 'لطفا از منوی زیر انتخاب کن', reply_markup=constants.KEYBOARD_MAIN)

def commanhandler(bot, update):
    chat_id = update.message.chat_id
    command_pre = update.message.text[1]
    command_post = update.message.text[2:]
    bot.sendChatAction(chat_id, action = 'typing')
    if (command_pre == 'q'):
        q_id = db.get_question_id_by_msgid(command_post)
        if (q_id == False):
            bot.sendMessage(chat_id=chat_id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
        else:
            questions.show_question(q_id, chat_id, bot)
    elif (command_pre == 'u'):
        users.show_user(bot, chat_id, int(command_post))
    else:
        bot.sendMessage(chat_id=chat_id,text='لطفا از منوی زیر انتخاب کن', reply_markup=constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def wrong_call_handler(bot, update):
    query = update.callback_query
    bot.sendMessage(chat_id=query.from_user.id, text='لطفا /skip را بزنید', reply_markup = constants.KEYBOARD_ANSWER_CANCEL)

def skip(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='برگشتی به منوی اصلی', reply_markup = constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print('Unauthorized')
    except BadRequest:
        print('BadRequest')
    except TimedOut:
        print('TimedOut')
    except NetworkError:
        print('NetworkError')
    except TelegramError:
        print('TelegramError')

def main():
    #db.create_database()
    # Create the EventHandler and pass it your bot's token.
    db.connect()
    updater = Updater(constants.TOKEN)
    # Get the dispatcher to register handlers

    main_conversationhandler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler([Filters.command], commanhandler),
                      MessageHandler([Filters.text], registered_user),
                      CallbackQueryHandler(functions.call_handler)],
        states={
            constants.STATE_MAIN: [MessageHandler([Filters.text], main_menue_handler),
                                   MessageHandler([Filters.command], commanhandler),
                                   CallbackQueryHandler(functions.call_handler)],

            constants.STATE_ASK:  [MessageHandler([Filters.text], questions.insert_question),
                                   CommandHandler('skip', questions.skip_question),
                                   CallbackQueryHandler(wrong_call_handler)],

            constants.STATE_ANSWER_INSERT: [MessageHandler([Filters.text], answers.insert_answer),
                                            CommandHandler('skip', answers.cancel_answer),
                                            CommandHandler('done', answers.finish_answer),
                                            CallbackQueryHandler(wrong_call_handler)],

            constants.STATE_ANSWER_EDIT: [MessageHandler([Filters.text], answers.edit_answer),
                                          CommandHandler('skip', answers.cancel_edit_answer),
                                          CommandHandler('done', answers.finish_edit_answer),
                                          CallbackQueryHandler(wrong_call_handler)],

            constants.STATE_COMMENT: [MessageHandler([Filters.text], comments.insert_comment),
                                      CommandHandler('skip', comments.cancel_comment),
                                      CallbackQueryHandler(wrong_call_handler)],

            constants.STATE_TOPIC: [MessageHandler([Filters.text], topics.insert_topic),
                                          CommandHandler('skip', questions.skip_question),
                                          CommandHandler('done', questions.finish_question),
                                          CallbackQueryHandler(wrong_call_handler)],

            constants.STATE_READ: [MessageHandler([Filters.text], questions.show),
                                   CommandHandler('skip', skip),
                                   CallbackQueryHandler(wrong_call_handler)],
        },
        fallbacks=[CommandHandler('stop', stop_this_fucking_bot)])

    dp = updater.dispatcher

    # on different commands - answer in Telegrm
    # add conversation handler
    # dp.add_handler(conv_question)
    # dp.add_handler(conv_answer)
    # dp.add_handler(cal_handler)
    dp.add_handler(main_conversationhandler)
    # on noncommand i.e message - echo the message on Telegram
    # log all errors
    dp.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
