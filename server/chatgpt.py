# -*- coding: utf-8 -*-
# @Project ：ChatGPT-Speech111
# @File ：ChatGPT-Speech111.py
# @Author ：XSM
# @Date ：2023/3/3 21:40
import os
from uuid import uuid4

import openai

from db import get_history_messages, insert_messages, insert_topic, get_topic, update_tokens
from server import logger

openai.api_key = os.environ.get('openai_key')
logger.info(f'初始化openai完成:{openai.api_key[0:10]} gpt-3.5-turbo-0301')
model = "gpt-3.5-turbo-0301"


def chatgpt(prompt, email=None, topic_id=None, ip='', max_len=100, max_tokens=2048):
    chat_id = 'chat:' + str(uuid4())
    if len(prompt) > max_len:
        prompt = prompt[0:max_len]
        logger.warning(f"问题过长: {prompt}")
        return f'The question is too long, please simplify or split it into multiple questions. ' \
               f'Each question should not exceed {max_len} characters.'
    if not prompt:
        return f'Please enter valid content!!!'
    if email is None:
        email = 'email:' + str(uuid4())
    logger.info([chat_id, email, topic_id, ip, prompt])
    # 获取 topic chat_history
    topic = get_topic(topic_id=topic_id, email=email)
    if topic_id is None:
        topic_id = topic[2]
    if topic_id is None:
        topic_id = set_topic(email=email, ip=ip)
    df_chat_history = get_history_messages(topic_id=topic_id, email=email)
    # 写入问题
    role = 'user'
    prompt_id = 'message:' + str(uuid4())
    insert_messages(data=(prompt_id, chat_id, topic_id, email, role, prompt, 0, ip))
    total_tokens = topic[1] + 14
    messages = [{"role": "system", "content": "简洁回答," + topic[0]}]
    for ind, row in df_chat_history.iterrows():
        total_tokens += row['tokens']
        if total_tokens >= (max_tokens - len(prompt) * 2):
            break
        else:
            messages.insert(1, {"role": row['role'], "content": row['content']})
    messages.append({"role": role, "content": prompt})
    # 获取答案
    response = openai.ChatCompletion.create(model=model, messages=messages, n=1, max_tokens=2048, frequency_penalty=0.5)
    texts = response['choices'][0]['message']['content']
    prompt_tokens = response['usage']['prompt_tokens'] - total_tokens
    completion_tokens = response['usage']['completion_tokens']
    completion_id = response['id']
    # 写入答案，更新问题token
    insert_messages(data=(completion_id, chat_id, topic_id, email, 'assistant', texts, completion_tokens, ip))
    update_tokens(prompt_id, prompt_tokens)
    logger.info([chat_id, email, topic_id, ip, prompt, response])
    return texts


def set_topic(topic=None, email=None, ip=''):
    if email is None:
        email = 'email:' + str(uuid4())
    logger.info([topic, email, ip])
    if topic:
        topic_ = get_topic(email=email, topic=topic)
        topic_id = topic_[2]
        if topic_id:
            return topic_id
        else:
            topic_id = 'topic:' + str(uuid4())
            role = 'system'
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": role, "content": topic}],
                max_tokens=3,
                n=1
            )
            tokens = response['usage']['prompt_tokens']
    else:
        topic_id = 'topic:' + str(uuid4())
        topic = ''
        tokens = 0
    insert_topic(topic_id, email, topic, tokens, ip)
    logger.info([topic, topic_id, email, ip, tokens])
    return topic_id


if __name__ == '__main__':
    # print(openai.Model.list('gpt'))
    r = chatgpt('用python写一个冒泡排序？并解析', email='email:dfee059e-d0be-4b4d-b283-f005bf6d0ac4')
    r = chatgpt('有没有更高效的方法？', email='email:dfee059e-d0be-4b4d-b283-f005bf6d0ac4')
    # print(set_topic(email='email:bd7e4fd8-a110-4248-a806-403e1aed67a6'))
    # print(r)
    # print(f'ChatGpt:{r}')
