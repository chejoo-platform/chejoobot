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
        bot.sendMessage(update.message.chat_id, text =" سلام {} جان خوش آمدی 😍\n.".format(from_user.first_name), reply_markup=constants.KEYBOARD_MAIN)
        topics.select_topics(bot, from_user.id)
        bot.sendMessage(update.message.chat_id, text =" اولین سوالی که واسه همه پیش میاد  اینه که این بات چجوری کار میکنه اگه میخوای جوابشو بدونی روی👈🏻 /q4827 بزن\n.", reply_markup=constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def stop_this_fucking_bot(bot, update):
    return ConversationHandler.END

def main_menue_handler(bot, update):
    message = update.message.text
    if (message == 'سوالای اخیر'):
        bot.sendMessage(update.message.chat_id,
                        text = 'از موضوعات زیر یکی را انتخاب کنید', reply_markup=constants.KEYBOARD_READ)
        db.unactivate(update.message.chat_id)
        return constants.STATE_READ
    elif (message == '🤔 از چجو بپرس'):
        if db.user_is_blocked(update.message.chat_id):
            bot.sendMessage(update.message.chat_id,
                            text = ' متاسفم شما بلاک شده اید و نمیتوانید ازین بات استفاده کنید', reply_markup=constants.KEYBOARD_MAIN)
            return constants.STATE_MAIN
        bot.sendMessage(update.message.chat_id,
                        text = ' سوال خود را وارد کن اگر منصرف شدی /skip رو بزن\n.', reply_markup=constants.KEYBOARD_ASK)
        db.unactivate(update.message.chat_id)
        return constants.STATE_ASK
    elif (message == '👤 پروفایل'):
        users.show_user(bot, update.message.chat_id, update.message.chat_id)
        return constants.STATE_MAIN
    elif (message == '⚙ تنظیمات'):
        topics.select_topics(bot, update.message.chat_id)
    elif (message == '🎗🎗🎗رنکینگ کاربران🎗🎗🎗'):
        users.show_top_users(bot, update.message.chat_id)
    elif (message == ''):
        show_how_to_work_with_bot(bot, update.message.chat_id)
    else:
        bot.sendMessage(update.message.chat_id, text = 'لطفا از منوی زیر انتخاب کنید', reply_markup=constants.KEYBOARD_MAIN)

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
        if command_post.isdigit():
            users.show_user(bot, chat_id, int(command_post))
        else:
            user_id = db.get_user_by_username(command_post)
            users.show_user(bot, chat_id, user_id)

    elif (command_pre == 'w'):
        if command_post.isdigit():
            questions.show_questions_asked_by_user(bot, chat_id, int(command_post))
        else:
            user_id = db.get_user_by_username(command_post)
            questions.show_questions_asked_by_user(bot, chat_id, user_id)

    elif (command_pre == 'v'):
        if command_post.isdigit():
            answers.show_best_answer_of_user(bot, chat_id, int(command_post))
        else:
            user_id = db.get_user_by_username(command_post)
            answers.show_best_answer_of_user(bot, chat_id, user_id)

    elif update.message.text == '/sendupdatemessage':
        bot.sendMessage(chat_id=chat_id,text='پیام آپدیت بات رو وارد کن', reply_markup=constants.KEYBOARD_MAIN)
        return constants.STATE_UPDATE

    elif update.message.text == '/top':
        users.show_top_users(bot, chat_id = chat_id)
    elif update.message.text == '/level':
        db.update_levels()
        bot.sendMessage(chat_id=chat_id,text='لول کاربران آپدیت شد', reply_markup=constants.KEYBOARD_MAIN)
    else:
        bot.sendMessage(chat_id=chat_id,text='لطفا از منوی زیر انتخاب کنید', reply_markup=constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def wrong_call_handler(bot, update):
    query = update.callback_query
    bot.answerCallbackQuery(query.id,text= 'این دکمه ها کار نمیکنن تا زمانی که برگردی به منوی اصلی')
    # bot.sendMessage(chat_id=query.from_user.id, text='شما در موقعیتی نیستید که بتوانید ازین دکمه ها استفاده کنید 😝لطفا /skip را بزنید تا ببینید چه کارهایی میتوانید انجام دهید😌', reply_markup = constants.KEYBOARD_ANSWER_CANCEL)

def skip(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='برگشتید به منوی اصلی', reply_markup = constants.KEYBOARD_MAIN)
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

def show_how_to_work_with_bot(bot, u_id):
    bot.sendMessage(chat_id=u_id, text= constants.HOW_TO_WORK_WITH_BOT)

def update_message(bot, update):
    for u in db.get_users():
        try:
            bot.sendMessage(chat_id=u['id'], text = update.message.text)
        except:
            db.unactivate(u['id'])
    bot.sendMessage(chat_id=update.message.chat_id,text='پیام آپدیت بات برای همه ارسال شد', reply_markup=constants.KEYBOARD_MAIN)
    return constants.STATE_MAIN

def send_bot_update_message_to_all_users(bot):
    for u in db.get_users():
        try:
            bot.sendMessage(chat_id=u['id'], text = constants.BOT_UPDATE_MESSAGE)
        except:
            db.unactivate(u['id'])

def main():
    #db.create_database()
    # Create the EventHandler and pass it your bot's token.
    db.connect()
    updater = Updater(constants.TOKEN)
    # Get the dispatcher to register handlers

    main_conversationhandler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler([Filters.command], commanhandler),
                      MessageHandler([Filters.text], main_menue_handler),
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

            constants.STATE_UPDATE: [MessageHandler([Filters.text], update_message)]
        },
        fallbacks=[CommandHandler('stop', stop_this_fucking_bot)])

    dp = updater.dispatcher

    # on different commands - answer in Telegrm
    # add conversation handler
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
