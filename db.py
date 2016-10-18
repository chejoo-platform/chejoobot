
# -*- coding: utf-8 -*-
import rethinkdb as r
import constants
import datetime
import pytz
import json


def connect():
    conn = r.connect(host=constants.DATABASE_HOST,db=constants.DATABASE_DATABASE)
    return conn
conn = connect()
def create_database():
    c = r.connect('localhost')
    if constants.DATABASE_DATABASE in r.db_list().run(c):
        pass
    else:
        r.db_create(constants.DATABASE_DATABASE).run(c)
    c.close()
    # conn = connect()
    for table in constants.DATABASE_TABLES:
        if table in r.table_list().run(conn):
            pass
        else:
            r.table_create(table).run(conn)
    # acitvate_all_users()
    # conn.close()

def insert_new_user(telid, first_name, last_name, username):
    # conn = connect()
    new_user = {"id": telid, "first_name": first_name, "last_name": last_name,
                "username": username, "active": True,
                "score": 0, "followers": [], "level" : 1,
                'a_numbers': 0, 'q_numbers': 0,
                'topics': list()}
    r.table("USERS").insert(new_user).run(conn)
    # follow_or_unfollow_topic(telid, 'پلتفرم')
    follow_or_unfollow_topic(telid, 'استارتاپ')
    # follow_or_unfollow_topic(telid, 'چجو')
    # follow_or_unfollow_topic(telid, 'متفرقه')
    # conn.close()

def deactivate_all_users():
    # conn = connect()
    r.table('USERS').update({'active': False}).run(conn)
    # conn.close()

def acitvate_all_users():
    # conn = connect()
    r.table('USERS').update({'active': True}).run(conn)
    # conn.close()

def unactivate(user):
    # conn = connect()
    r.table('USERS').get(user).update({'active': False}).run(conn)
    # conn.close()

def activate(user):
    # conn = connect()
    r.table('USERS').get(user).update({'active': True}).run(conn)
    # conn.close()

def user_is_active(u_id):
    return r.table('USERS').get(u_id).run(conn)['active']

def user_is_admin(u_id):
    # conn = connect()
    x = r.table("ADMINS").get(u_id).run(conn)
    if x == None:
        return False
    else:
        return True

def add_to_admins(u_id):
    # conn = connect()
    r.table('ADMINS').insert({'id': u_id}).run(conn)
    # conn.close()

def check_user(telid):
    # conn = connect()
    x = r.table('USERS').get(telid).run(conn)
    if x == None:
        return False
    else:
        return True

def get_user(telid):
    # conn = connect()
    x = r.table('USERS').get(telid).run(conn)
    # conn.close()
    return x

def get_user_by_username(username):
    x = list(r.table('USERS').filter({'username': username}).run(conn))[0]['id']
    return x

def get_users():
    x = r.table('USERS').filter({'active': True}).run(conn)
    return x

def get_users_followed_topic(topic):
    x = r.table('USERS').filter({'active': True}).filter(lambda user:user['topics'].contains(topic)).run(conn)
    return x

def follow_or_unfollow_user(u_id, follower_id):
    # if (u_id == follower_id):
        # return True
    # conn = connect()
    user = r.table('USERS').get(u_id).run(conn)
    follower_level = r.table('USERS').get(follower_id).run(conn)['level']
    score = user['score']
    followers = set(user['followers'])
    if follower_id in followers:
        followers.remove(follower_id)
        score -= 2 * follower_level
    else:
        followers.add(follower_id)
        score += 2 * follower_level
    r.table('USERS').get(u_id).update({'followers': list(followers), 'score': score}).run(conn)
    update_level_of_user(u_id)
    return (follower_id in followers)
    # conn.close()

def get_ranked_user(sk):
    user = list(r.table('USERS').order_by(r.desc('score')).skip(sk).limit(1).run(conn))[0]
    return user

def user_is_blocked(u_id):
    x = r.table("BLOCKED").get(u_id).run(conn)
    if x == None:
        return False
    else:
        return True

def get_user_numbers():
    return len(list(r.table('USERS').run(conn)))

def block_user(u_id):
    r.table('BLOCKED').insert({'id': u_id, 'date': r.now()}).run(conn)

def unblock_user(u_id):
    r.table('BLOCKED').get(u_id).delete().run(conn)

def insert_new_question(idd, text, userid, date):
    # conn = connect()
    new_question = {"id": str(idd)+'-'+str(userid) ,"msg_id": idd, "question": text, "user_id": userid, 'date': pytz.utc.localize(date), 'followers': [userid], 'answers': list()}
    r.table('QUESTIONS').insert(new_question).run(conn)
    user = r.table('USERS').get(userid)
    q_numbers = user.run(conn)['q_numbers']+1
    user.update({'q_numbers': q_numbers }).run(conn)
    # conn.close()

def insert_question_to_temp(msg_id, text, u_id, date):
    # conn = connect()
    new_question = {"id": u_id ,"msg_id": msg_id, "question": text, "user_id": u_id, 'date': r.now(), 'followers': list(), 'answers': list(), 'topics': list()}
    r.table('TEMP').insert(new_question).run(conn)
    # conn.close()

def insert_topic_to_temp(user_id, topic):
    # conn = connect()
    old_topic = r.table('TEMP').get(user_id).run(conn)['topics']
    old_topic.append(topic)
    up_topic = {'topics': old_topic}
    r.table('TEMP').get(user_id).update(up_topic).run(conn)
    # conn.close()

def push_question_from_temp_to_questions(user_id):
    # conn = connect()
    touple = r.table('TEMP').get(user_id).run(conn)
    new_id = str(touple['msg_id'])+'-'+str(user_id)
    touple['id'] = new_id
    r.table('TEMP').get(user_id).delete().run(conn)
    r.table('QUESTIONS').insert(touple).run(conn)
    user = r.table('USERS').get(user_id)
    q_numbers = user.run(conn)['q_numbers']+1
    user.update({'q_numbers': q_numbers }).run(conn)
    return new_id

def empty_temp(u_id):
    r.table('TEMP').get(u_id).delete().run(conn)


def follow_or_unfollow_question(q_id, user_id):
    # conn = connect()
    question = r.table('QUESTIONS').get(q_id).run(conn)
    asker = r.table('USERS').get(question['user_id']).run(conn)
    follower = r.table('USERS').get(user_id).run(conn)
    score = asker['score']
    followers = set(question['followers'])
    if user_id in followers:
        followers.remove(user_id)
        score -= follower['level']
    else:
        followers.add(user_id)
        score += follower['level']
    r.table('QUESTIONS').get(q_id).update({'followers': list(followers)}).run(conn)
    r.table('USERS').get(question['user_id']).update({'score': score}).run(conn)
    update_level_of_user(question['user_id'])
    return (user_id in followers)
    # conn.close()

def get_followers_question(q_id):
    # conn = connect()
    followers = r.table('QUESTIONS').get(q_id).run(conn)['followers']
    # conn.close()
    return followers

def get_question(q_id):
    # conn = connect()
    question = r.table('QUESTIONS').get(q_id).run(conn)
    # conn.close()
    return question

def get_question_id_by_msgid(msgid):
    # conn = connect()
    question = r.table('QUESTIONS').filter({'msg_id': int(msgid)})
    if (question.is_empty().run(conn)):
        return False
    else:
        return list(question.run(conn))[0]['id']
    # conn.close()

def delete_question(q_id):
    # conn = connect()
    r.table('QUESTIONS').get(q_id).delete().run(conn)
    user_id = int(q_id.split('-')[1])
    user = r.table('USERS').get(user_id)
    q_numbers = user.run(conn)['q_numbers']-1
    user.update({'q_numbers': q_numbers }).run(conn)
    # conn.close()

def delete_answers_of_question(q_id):
    r.table('ANSWERS').filter({'q_id': q_id}).delete().run(conn)

def get_last_questions(n, s, topic):
    # conn = connect()
    if (topic == 'همه'):
        questions = r.table('QUESTIONS').order_by(r.desc('date')).skip(s).limit(n).run(conn)
    else:
        questions = r.table('QUESTIONS').filter(lambda q: q['topics'].contains(topic)).order_by(r.desc('date')).skip(s).limit(n).run(conn)
    # conn.close()
    return questions

def get_topic_of_question(q_id):
    topics = r.table('QUESTIONS').get(q_id).run(conn)['topics']
    return topics[0]

def get_questions_of_user(u_id, s, n):
    questions = r.table('QUESTIONS').filter({'user_id': u_id}).order_by(r.desc('date')).skip(s).limit(n).run(conn)
    return questions

def insert_answer_to_temp_edit(user_id, q_id):
    # conn = connect()
    x = r.table('ANSWERS').get(str(q_id)+'-'+str(user_id)).run(conn)
    new_answer = {'id': user_id, 'q_id': q_id, 'text': ''}
    r.table('TEMP').insert(new_answer).run(conn)
    # conn.close()

def insert_answer_to_temp(user_id, q_id):
    # conn = connect()
    new_answer = {'id': user_id, 'q_id': q_id, 'text': '',
                  'upvotes': 0 , 'upvoters': list(),
                  'downvotes': 0, 'downvoters': list(),
                  'up_and_down': 0, 'date': r.now(),
                  'comments': list()}
    r.table('TEMP').insert(new_answer).run(conn)
    # conn.close()

def update_answer_of_temp(user_id, text):
    # conn = connect()
    old_text = r.table('TEMP').get(user_id).run(conn)['text']
    new_text = old_text + '\n' + text
    up_answer = {'text': new_text}
    r.table('TEMP').get(user_id).update(up_answer).run(conn)
    # conn.close()

def push_answer_form_temp_to_answers(user_id):
    # conn = connect()
    touple = r.table('TEMP').get(user_id).run(conn)
    q_id = touple['q_id']
    question = r.table('QUESTIONS').get(q_id).run(conn)
    answers = question['answers']
    touple['u_id'] = user_id
    new_id = q_id+"-"+str(user_id)
    touple['id'] = new_id
    r.table('TEMP').get(user_id).delete().run(conn)
    r.table('ANSWERS').insert(touple).run(conn)
    answers.append(new_id)
    r.table('QUESTIONS').get(q_id).update({'answers': answers}).run(conn)
    user = r.table('USERS').get(user_id)
    a_numbers = user.run(conn)['a_numbers'] + 1
    user.update({'a_numbers': a_numbers }).run(conn)
    # conn.close()
    return q_id, new_id

def push_answer_form_temp_to_answers_edit_mod(user_id):
    # conn = connect()
    touple = r.table('TEMP').get(user_id).run(conn)
    q_id = touple['q_id']
    new_id = q_id+"-"+str(user_id)
    touple['u_id'] = user_id
    touple['id'] = new_id
    r.table('TEMP').get(user_id).delete().run(conn)
    r.table('ANSWERS').get(new_id).update(touple).run(conn)
    user = r.table('USERS').get(user_id)
    # conn.close()
    return q_id, new_id

def del_answer_from_temp(user_id):
    # conn = connect()
    q_id = r.table('TEMP').get(user_id).run(conn)['q_id']
    r.table('TEMP').get(user_id).delete().run(conn)
    # conn.close()
    return q_id

def get_answers(q_id):
    # conn = connect()
    answers = r.table('ANSWERS').filter({'q_id': q_id}).order_by(r.desc('up_and_down')).run(conn)
    # conn.close()
    return answers

def have_answer(q_id):
    # conn = connect()
    answers = len(list(r.table('ANSWERS').filter({'q_id': q_id}).run(conn)))
    # conn.close()
    if (answers == 0):
        return False
    else:
        return True

def upvote_answer(an_id, user_id):
    # conn = connect()
    writer_id = int(an_id.split("-")[2])
    user_level = r.table('USERS').get(user_id).run(conn)['level']
    writer = r.table('USERS').get(writer_id).run(conn)
    writer_score = writer['score']
    answer = r.table('ANSWERS').get(an_id).run(conn)
    upvoters = set(answer['upvoters'])
    upvotes = answer['upvotes']
    downvoters = set(answer['downvoters'])
    downvotes = answer['downvotes']
    up_and_down = answer['up_and_down']
    if user_id in downvoters:
        downvoters.remove(user_id)
        downvotes -= user_level
        up_and_down += user_level
    if user_id in upvoters:
        upvoters.remove(user_id)
        upvotes -= user_level
        up_and_down -= user_level
        writer_score -= user_level
    else:
        upvoters.add(user_id)
        upvotes += user_level
        up_and_down += user_level
        writer_score += user_level
    r.table('USERS').get(writer_id).update({'score': writer_score}).run(conn)
    r.table('ANSWERS').get(an_id).update({'downvotes': downvotes, 'downvoters': list(downvoters),
                                          'upvoters': list(upvoters), 'upvotes': upvotes,
                                          'up_and_down': up_and_down}).run(conn)
    update_level_of_user(writer_id)
    # conn.close()
    return upvotes

def downvote_answer(an_id, user_id):
    # conn = connect()
    writer_id = int(an_id.split("-")[2])
    user_level = r.table('USERS').get(user_id).run(conn)['level']
    writer = r.table('USERS').get(writer_id).run(conn)
    writer_score = writer['score']
    answer = r.table('ANSWERS').get(an_id).run(conn)
    upvoters = set(answer['upvoters'])
    downvoters = set(answer['downvoters'])
    upvotes = answer['upvotes']
    downvotes = answer['downvotes']
    up_and_down = answer['up_and_down']
    if user_id in upvoters:
        upvoters.remove(user_id)
        upvotes -= user_level
        up_and_down -= user_level
        writer_score -= user_level
    if user_id in downvoters:
        downvoters.remove(user_id)
        downvotes -= user_level
        up_and_down += user_level
    else:
        downvoters.add(user_id)
        downvotes += user_level
        up_and_down -= user_level
    r.table('USERS').get(writer_id).update({'score': writer_score}).run(conn)
    r.table('ANSWERS').get(an_id).update({'downvotes': downvotes, 'downvoters': list(downvoters),
                                          'upvoters': list(upvoters), 'upvotes': upvotes,
                                          'up_and_down': up_and_down}).run(conn)
    update_level_of_user(writer_id)
    # conn.close()
    return upvotes

def delete_table(table):
    # conn = connect()
    r.table_drop(table).run(conn)
    # conn.close()

def user_have_answered(q_id, u_id):
    # conn = connect()
    ans = r.table('ANSWERS').get(str(q_id)+'-'+str(u_id)).run(conn)
    # conn.close()
    if (ans == None):
        return False
    else:
        return True

def get_answer(an_id):
    # conn = connect()
    ans = r.table('ANSWERS').get(an_id).run(conn)
    # conn.close()
    return ans

def get_answer_upvoters(an_id):
    upvoters = r.table('ANSWERS').get(an_id).run(conn)['upvoters']
    return upvoters

def get_best_answer_of_this_user(u_id):
    answer = list(r.table('ANSWERS').filter({'u_id': u_id}).order_by(r.desc('up_and_down')).limit(1).run(conn))
    if len(answer) == 0:
        return False
    return answer[0]

def get_comments(an_id):
    # conn = connect()
    c = r.table('COMMENTS').filter({'an_id': an_id}).order_by(r.desc('date')).limit(7).run(conn)
    return c

def insert_comment_to_temp(u_id, an_id):
    # conn = connect()
    r.table('TEMP').insert({'id': u_id, 'an_id': an_id}).run(conn)
    # conn.close()

def insert_comment(user_id, text):
    # conn = connect()
    an_id = r.table('TEMP').get(user_id).run(conn)['an_id']
    x = r.table('COMMENTS').insert({'an_id': an_id,
                                'text': text,
                                'u_id': user_id,
                                'date': r.now()}).run(conn)['generated_keys'][0]
    comments = r.table('ANSWERS').get(an_id).run(conn)['comments']
    comments.append(x)
    r.table('ANSWERS').get(an_id).update({'comments': comments}).run(conn)
    # conn.close()
    del_comment_from_temp(user_id)
    return an_id, x

def del_comment_from_temp(u_id):
    # conn = connect()
    # an_id = r.table('TEMP').get(u_id).run(conn)['an_id']
    r.table('TEMP').get(u_id).delete().run(conn)
    # conn.close()
    # return an_id

def get_comment(c_id):
    # conn = connect()
    comment = r.table('COMMENTS').get(c_id).run(conn)
    # conn.close()
    return comment

def get_user_topics(u_id):
    topics = r.table('USERS').get(u_id).run(conn)['topics']
    return topics

def follow_or_unfollow_topic(u_id, topic):
    topics = r.table('USERS').get(u_id).run(conn)['topics']
    t=r.table('TOPICS').get(topic).run(conn)
    f_number = t['f_number']
    if topic in topics:
        topics.remove(topic)
        f_number -= 1
    else:
        topics.append(topic)
        f_number += 1
    r.table('TOPICS').get(topic).update({'f_number': f_number}).run(conn)
    r.table('USERS').get(u_id).update({'topics': topics}).run(conn)
    return (topic in topics)

def topic_follower_number(topic):
    f_number =r.table('TOPICS').get(topic).run(conn)['f_number']
    return f_number

def update_users():
    acitvate_all_users()
    for user in get_users():
        score = 0
        for q in r.table('QUESTIONS').filter({'user_id': user['id']}).run(conn):
            score += len(q['followers'])
        for a in r.table('ANSWERS').filter({'u_id': user['id']}).run(conn):
            score += a['upvotes']
        for u in user['followers']:
            f_level = r.table('USERS').get(u).run(conn)['level']
            score += 2 * f_level
        r.table('USERS').get(user['id']).update({'score': score}).run(conn)

def delete_answers_without_questions():
    for a in r.table("ANSWERS").run(conn):
        q_id = a['q_id']
        an_id = a['id']
        if r.table('QUESTIONS').get(q_id).run(conn) == None:
            r.table('ANSWERS').get(an_id).delete().run(conn)

def update_topic_follow_number():
    p_f_num = len(list(r.table('USERS').filter(lambda user: user['topics'].contains('پلتفرم')).run(conn)))
    c_f_num = len(list(r.table('USERS').filter(lambda user: user['topics'].contains('چجو')).run(conn)))
    o_f_num = len(list(r.table('USERS').filter(lambda user: user['topics'].contains('متفرقه')).run(conn)))
    s_f_num = len(list(r.table('USERS').filter(lambda user: user['topics'].contains('استارتاپ')).run(conn)))
    r.table('TOPICS').get('پلتفرم').update({'f_number': p_f_num}).run(conn)
    r.table('TOPICS').get('استارتاپ').update({'f_number': s_f_num}).run(conn)
    r.table('TOPICS').get('چجو').update({'f_number': c_f_num}).run(conn)
    r.table('TOPICS').get('متفرقه').update({'f_number': o_f_num}).run(conn)

def get_level(score):
    if score < constants.LEVEL_STAGES[0]:
        return 1
    elif score < constants.LEVEL_STAGES[1]:
        return 2
    elif score < constants.LEVEL_STAGES[2]:
        return 3
    elif score < constants.LEVEL_STAGES[3]:
        return 4
    elif score < constants.LEVEL_STAGES[4]:
        return 5
    elif score < constants.LEVEL_STAGES[5]:
        return 6
    elif score < constants.LEVEL_STAGES[6]:
        return 7
    elif score < constants.LEVEL_STAGES[7]:
        return 8
    elif score < constants.LEVEL_STAGES[8]:
        return 9
    elif score < constants.LEVEL_STAGES[9]:
        return 10
    else:
        return 11

def update_level_of_user(u_id):
    u = r.table('USERS').get(u_id).run(conn)
    level = get_level(u['score'])
    r.table('USERS').get(u_id).update({'level': level}).run(conn)

def update_levels():
    for u in r.table('USERS').run(conn):
        level = get_level(u['score'])
        r.table('USERS').get(u['id']).update({'level': level}).run(conn)

if __name__ == '__main__' :
    create_database()
    r.table('TEMP').delete().run(conn)
    delete_answers_without_questions()
    # update_users()
