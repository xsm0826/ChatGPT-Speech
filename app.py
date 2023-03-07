# -*- coding: utf-8 -*-
# @Project ：ChatGPT-Speech111
# @File ：app.py
# @Author ：XSM
# @Date ：2023/3/3 23:43
import hashlib

import markdown
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory

from api.chat import api_chat
from api.voice import api_voice
from db import find_user, create_user
from server.chatgpt import chatgpt, set_topic

app = Flask('CRAZY_GPT')
app.secret_key = "mysecretkey"


@app.route("/")
def index():
    if "email" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


@app.route("/connect")
def connect():
    return 'Chat with us by xsm0826@126.com.'


@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = find_user(email)
        if user is None:
            error = "Invalid email or password"
        else:
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
            if user[2] != hashed_password:
                error = "Invalid email or password"
            elif user[3] != 1:
                error = "Invalid account status! Chat with us by xsm0826@126.com."
            else:
                session["email"] = email
                return redirect(url_for("index"))
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "email" in session:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = find_user(email)
        if user is not None:
            error = "Invalid email or password"
        else:
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
            ip = request.remote_addr
            create_user(email, hashed_password, ip)
            return redirect(url_for("login"))
    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))


@app.route("/test_page")
def test_page():
    if "email" in session:
        return render_template("test_page.html")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.register_blueprint(api_chat, url_prefix='/')
    app.register_blueprint(api_voice, url_prefix='/')
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)
