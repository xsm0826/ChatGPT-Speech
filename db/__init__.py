# -*- coding: utf-8 -*-
# @Project ：ChatGPT-Speech111
# @File ：__init__.py.py
# @Author ：XSM
# @Date ：2023/3/4 10:51
import sqlite3
import pandas as pd

from server import logger

file_db = r'/\db\chatgpt.db'


def create_tables():
    conn = sqlite3.connect(file_db)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, 
    email TEXT UNIQUE, 
    password TEXT, 
    ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")
    conn.close()


def find_user(email):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id,email,password,status FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def create_user(email, hashed_password, ip=''):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO users (email, password,ip) VALUES (?, ?,?)", (email, hashed_password, ip))
    conn.commit()
    cursor.close()
    conn.close()


def get_history_messages(topic_id=None, email=None):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    if topic_id is not None:
        df = pd.read_sql(
            f"""SELECT `role`,content,tokens FROM messages where topic_id = '{topic_id}' and `role` in ('user','assistant')
            order by id desc limit 20;""", conn)
    elif email is not None:
        df = pd.read_sql(
            f"""SELECT `role`,content,tokens FROM messages where email = '{email}'  and `role` in ('user','assistant')
            order by id desc limit 20;""", conn)
    else:
        df = pd.DataFrame(columns=['role', 'content', 'tokens'])
    cursor.close()
    conn.close()
    return df


def insert_messages(data=('message_id', 'chat_id', 'topic_id', 'email', 'role', 'content', 0, 'ip')):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO messages (message_id, chat_id, topic_id, email, role, content, tokens, ip) 
                VALUES (?, ? ,?, ?,?, ? ,?, ?)""", data)
    conn.commit()
    cursor.close()
    conn.close()


def update_tokens(message_id, tokens):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE messages set tokens = {tokens} where message_id = '{message_id}';")
    conn.commit()
    cursor.close()
    conn.close()


def insert_topic(topic_id, email, content, tokens, ip):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO topic (topic_id,email,content,tokens,ip) VALUES (?, ? ,?, ?,?)",
                   (topic_id, email, content, tokens, ip))
    conn.commit()
    cursor.close()
    conn.close()


def get_topic(topic_id=None, email=None, topic=None):
    conn = sqlite3.connect(file_db)
    cursor = conn.cursor()
    if topic is not None and email is not None:
        df = pd.read_sql(
            f"""SELECT topic_id,content,tokens FROM topic  where email = '{email}' and content like '%{topic}%'
                                order by id desc limit 1;""", conn)
    elif topic_id is not None:
        df = pd.read_sql(f"""SELECT topic_id,content,tokens FROM topic  where topic_id = '{topic_id}'""", conn)
    elif email is not None:
        df = pd.read_sql(f"""SELECT topic_id,content,tokens FROM topic  where email = '{email}' 
                                order by id desc limit 1;""", conn)
    else:
        df = pd.DataFrame(columns=['topic_id', 'content', 'tokens'])
    cursor.close()
    conn.close()
    if len(df) == 0:
        return '', 0, None
    else:
        return df.content.iloc[0], df.tokens.iloc[0], df.topic_id.iloc[0]


create_tables()
logger.info(f'初始化sqlite完成:{file_db}')

if __name__ == '__main__':
    # insert_messages()
    # update_tokens('message_id', 1)
    # print(get_topic('topic:4443e275-7aca-4cdd-9784-1a1c27fceb0d'))
    # print(get_topic(email='email:bd7e4fd8-a110-4248-a806-403e1aed67a6'))
    # print(create_tables())
    print(get_history_messages('123'))
    # create_user('email', 'hashed_password')
    # print(find_user('123'))
    # insert_messages(email='1', type_='q', content='b')
    # cursor.execute('drop table users;')
    # print(pd.read_sql("""SELECT type,name FROM sqlite_master;""", conn))
    # print(pd.read_sql("""SELECT * FROM users;""", conn))
    # print(pd.read_sql("""SELECT * FROM messages;""", conn))
    # df = pd.DataFrame([{'a': 1, 'b': 2}, {'a': 1, 'b': 2}])
    # df.to_sql(name='users', con=conn, if_exists='replace', index=False)
