# -*- coding: utf-8 -*-
# @Project ：ChatGPT-Speech
# @File ：chat.py
# @Author ：XSM
# @Date ：2023/3/5 18:00
from flask import Blueprint, session, redirect, url_for, request

from server.chatgpt import set_topic, chatgpt

api_chat = Blueprint('api_chat', 'chat')


@api_chat.route("chat")
def chat():
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    userText = request.args.get('msg', None)
    ip = request.remote_addr
    if 'topic:' == userText[0:6] or 'topic：' == userText[0:6]:
        topic_str = userText[6:]
        if not topic_str:
            return 'Please enter valid content!!!'
        elif all([i == ' ' for i in topic_str]):
            return 'Please enter valid content!!!'
        elif len(topic_str) > 20:
            return 'The content is too long!!!Less then 20 characters!!!'
        else:
            session["topic"] = set_topic(topic_str, email, ip=ip)
            return f'Set topic [{topic_str}] success!'
    topic_id = session.get("topic", None)
    chat_res = chatgpt(prompt=userText, email=email, topic_id=topic_id, ip=ip)
    # return markdown.markdown(str(chat_res))
    return str(chat_res).replace('\n', '<br/>').replace(' ', '&nbsp')
