
# -*- coding: utf-8 -*-
import rethinkdb as r
import constants
import datetime
import pytz
import json


def connect():
    conn = r.connect(host=constants.DATABASE_HOST,db=constants.DATABASE_DATABASE)
    return conn

def create_database():
    c = r.connect('localhost')
    if constants.DATABASE_DATABASE in r.db_list().run(c):
        pass
    else:
        r.db_create(constants.DATABASE_DATABASE).run(c)
    c.close()
    conn = connect()
    for table in constants.DATABASE_TABLES:
        if table in r.table_list().run(conn):
            pass
        else:
            r.table_create(table).run(conn)
    r.table_create('ANSWERS').update({'upvotes': 0, 'upvoters': []})
    add_to_admins(54659968)
    deactivate_all_users()
    conn.close()

def insert_new_user(telid, first_name, last_name, username):
    conn = connect()
    new_user = {"id": telid, "first_name": first_name, "last_name": last_name \
                             , "username": username, "active": True}
    r.table("USERS").insert(new_user).run(conn)
    conn.close()

def deactivate_all_users():
    conn = connect()
    r.table('USERS').update({'active': False}).run(conn)
    conn.close()

def acitvate_all_users():
    conn = connect()
    r.table('USERS').update({'active': True}).run(conn)
    conn.close()

def unactivate(user):
    conn = connect()
    r.table('USERS').get(user).update({'active': False}).run(conn)
    conn.close()

def activate(user):
    conn = connect()
    r.table('USERS').get(user).update({'active': True}).run(conn)
    conn.close()

def user_is_admin(u_id):
    conn = connect()
    x = r.table("ADMINS").get(u_id).run(conn)
    if x == None:
        return ''
    else:
        return 'حذف'

def add_to_admins(u_id):
    conn = connect()
    r.table('ADMINS').insert({'id': u_id}).run(conn)
    conn.close()

def check_user(telid):
    conn = connect()
    x = r.table('USERS').get(telid).run(conn)
    if x == None:
        return False
    else:
        return True

def get_user(telid):
    conn = connect()
    x = r.table('USERS').get(telid).run(conn)
    conn.close()
    return x

def get_users():
    conn = connect()
    x = r.table('USERS').filter({'active': True}).run(conn)
    conn.close()
    return x

def insert_new_question(idd, text, userid, date):
    conn = connect()
    new_question = {"id": str(idd)+'-'+str(userid) ,"msg_id": idd, "question": text, "user_id": userid, 'date': pytz.utc.localize(date), 'followers': [userid], 'answers': []}
    r.table('QUESTIONS').insert(new_question).run(conn)
    conn.close()

def follow_or_unfollow_question(q_id, user_id):
    conn = connect()
    questions = r.table('QUESTIONS').get(q_id).run(conn)
    followers = set(questions['followers'])
    if user_id in followers:
        followers.remove(user_id)
    else:
        followers.add(user_id)
    r.table('QUESTIONS').get(q_id).update({'followers': list(followers)}).run(conn)
    conn.close()

def get_followers_question(q_id):
    conn = connect()
    followers = r.table('QUESTIONS').get(q_id).run(conn)['followers']
    conn.close()
    return followers

def get_question(q_id):
    conn = connect()
    question = r.table('QUESTIONS').get(q_id).run(conn)
    conn.close()
    return question

def get_question_id_by_msgid(msgid):
    conn = connect()
    question = r.table('QUESTIONS').filter({'msg_id': int(msgid)})
    if (question.is_empty().run(conn)):
        return False
    else:
        return list(question.run(conn))[0]['id']
    conn.close()

def delete_question(q_id):
    conn = connect()
    r.table('QUESTIONS').get(q_id).delete().run(conn)
    conn.close()

def get_last_questions(n, s):
    conn = connect()
    questions = r.table('QUESTIONS').order_by(r.desc('date')).skip(s).limit(n).run(conn)
    conn.close()
    return questions

def insert_answer_to_temp_edit(user_id, q_id):
    conn = connect()
    x = r.table('ANSWERS').get(str(q_id)+'-'+str(user_id)).run(conn)
    last_votes = x['upvotes']
    last_voters = x['upvoters']
    new_answer = {'id': user_id, 'q_id': q_id, 'text': '', 'upvotes': last_votes, 'upvoters': last_voters}
    r.table('TEMP').insert(new_answer).run(conn)
    conn.close()

def insert_answer_to_temp(user_id, q_id):
    conn = connect()
    new_answer = {'id': user_id, 'q_id': q_id, 'text': '','upvotes': 0 , 'upvoters': [], 'downvotes': 0, 'downvoters': [], 'date': r.now()}
    r.table('TEMP').insert(new_answer).run(conn)
    conn.close()

def update_answer_of_temp(user_id, text):
    conn = connect()
    old_text = r.table('TEMP').get(user_id).run(conn)['text']
    new_text = old_text + '\n' + text
    up_answer = {'text': new_text}
    r.table('TEMP').get(user_id).update(up_answer).run(conn)
    conn.close()

def push_answer_form_temp_to_answers(user_id):
    conn = connect()
    touple = r.table('TEMP').get(user_id).run(conn)
    q_id = touple['q_id']
    answers = set(r.table('QUESTIONS').get(q_id).run(conn)['answers'])
    new_id = q_id+"-"+str(user_id)
    touple['id'] = new_id
    r.table('TEMP').get(user_id).delete().run(conn)
    if (r.table('ANSWERS').get(new_id).run(conn) == None):
        r.table('ANSWERS').insert(touple).run(conn)
        answers.add(new_id)
        r.table('QUESTIONS').get(q_id).update({'answers': list(answers)}).run(conn)
    else:
        r.table('ANSWERS').get(new_id).update(touple).run(conn)
    conn.close()
    return q_id, new_id

def del_answer_from_temp(user_id):
    conn = connect()
    q_id = r.table('TEMP').get(user_id).run(conn)['q_id']
    r.table('TEMP').get(user_id).delete().run(conn)
    conn.close()
    return q_id

def get_answers(q_id):
    conn = connect()
    answers = r.table('ANSWERS').filter({'q_id': q_id}).order_by(r.desc('upvotes')).run(conn)
    conn.close()
    return answers

def have_answer(q_id):
    conn = connect()
    answers = len(list(r.table('ANSWERS').filter({'q_id': q_id}).run(conn)))
    conn.close()
    if (answers == 0):
        return False
    else:
        return True

def upvote_answer(an_id, user_id):
    conn = connect()
    answer = r.table('ANSWERS').get(an_id).run(conn)
    upvoters = set(answer['upvoters'])
    upvotes = answer['upvotes']
    downvoters = set(answer['downvoters'])
    downvotes = answer['downvotes']
    if user_id in downvoters:
        downvoters.remove(user_id)
        downvotes -= 1
    if user_id in upvoters:
        upvoters.remove(user_id)
        upvotes -= 1
    else:
        upvoters.add(user_id)
        upvotes += 1
    r.table('ANSWERS').get(an_id).update({'downvotes': downvotes, 'downvoters': list(downvoters), 'upvoters': list(upvoters), 'upvotes': upvotes}).run(conn)
    conn.close()
    return upvotes

def downvote_answer(an_id, user_id):
    conn = connect()
    answer = r.table('ANSWERS').get(an_id).run(conn)
    upvoters = set(answer['upvoters'])
    downvoters = set(answer['downvoters'])
    upvotes = answer['upvotes']
    downvotes = answer['downvotes']
    if user_id in upvoters:
        upvoters.remove(user_id)
        upvotes -= 1
    if user_id in downvoters:
        downvoters.remove(user_id)
        downvotes -= 1
    else:
        downvoters.add(user_id)
        downvotes += 1
    r.table('ANSWERS').get(an_id).update({'downvotes': downvotes, 'downvoters': list(downvoters), 'upvoters': list(upvoters), 'upvotes': upvotes}).run(conn)
    conn.close()
    return upvotes

def delete_table(table):
    conn = connect()
    r.table_drop(table).run(conn)
    conn.close()

def user_have_answered(q_id, u_id):
    conn = connect()
    ans = r.table('ANSWERS').get(str(q_id)+'-'+str(u_id)).run(conn)
    conn.close()
    if (ans == None):
        return False
    else:
        return True

def get_answer(an_id):
    conn = connect()
    ans = r.table('ANSWERS').get(an_id).run(conn)
    conn.close()
    return ans

if __name__ == '__main__' :
    create_database()
