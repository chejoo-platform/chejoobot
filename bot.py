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
        print(update.message)
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
        questions.show_last_questions(bot,update.message.chat_id)
        return constants.STATE_MAIN
    elif (message == '🤔 از چجو بپرس'):
        bot.sendMessage(update.message.chat_id,
                        text = ' سوال خودت رو وارد کن یا اگه سوال نداری /skip رو بزن\n.', reply_markup=constants.KEYBOARD_ASK)
        return constants.STATE_ASK
    elif (message == '👤 پروفایل'):
        return constants.STATE_MAIN
    else:
        bot.sendMessage(update.message.chat_id, text = 'لطفا از منوی زیر انتخاب نمایید', reply_markup=constants.KEYBOARD_MAIN)

def commanhandler(bot, update):
    chat_id = update.message.chat_id
    command_pre = update.message.text[1]
    command_post = update.message.text[2:]
    if (command_pre == 'q'):
        q_id = db.get_question_id_by_msgid(command_post)
        if (q_id == False):
            bot.sendMessage(chat_id=chat_id,text='سوال حذف شده است🤗', reply_markup=constants.KEYBOARD_MAIN)
        else:
            questions.show_question(q_id, chat_id, bot)
    if (command_pre == 'u'):
        users.show_user(bot, chat_id, int(command_post))
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
    updater = Updater(constants.TOKEN)
    # Get the dispatcher to register handlers

    main_conversationhandler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler([Filters.text], registered_user),
                      CallbackQueryHandler(functions.call_handler)],
        states={
            constants.STATE_MAIN: [MessageHandler([Filters.text],
                                                  main_menue_handler),
                                   MessageHandler([Filters.command],
                                                  commanhandler),
                                   CallbackQueryHandler(functions.call_handler)],
            constants.STATE_ASK:  [MessageHandler([Filters.text],
                                                  questions.insert_question),
                                   CommandHandler('skip',
                                                  questions.skip_question)],
            constants.STATE_ANSWER_INSERT: [MessageHandler([Filters.text],
                                                           answers.insert_answer),
                                            CommandHandler('skip',
                                                           answers.cancel_answer),
                                            CommandHandler('done',
                                                           answers.finish_answer)],
            constants.STATE_ANSWER_EDIT: [MessageHandler([Filters.text],
                                                         answers.edit_answer),
                                            CommandHandler('skip',
                                                           answers.cancel_edit_answer),
                                            CommandHandler('done',
                                                           answers.finish_edit_answer)]},
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
