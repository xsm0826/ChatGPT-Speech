# -*- coding: utf-8 -*-
# @Project ：ChatGPT-Speech111
# @File ：voice.py
# @Author ：XSM
# @Date ：2023/3/5 18:00
import time
from io import BytesIO
from uuid import uuid4
from google.cloud import speech_v1p1beta1 as speech
from flask import Blueprint, session, redirect, url_for, request, send_file, render_template, jsonify
from gtts import gTTS

from server import logger

api_voice = Blueprint('api_voice', 'voice')


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "my-creds.json"


@api_voice.route("text2voice", methods=['POST', 'GET'])
def text2voice():
    if "email" not in session:
        return redirect(url_for("login"))
    email = session["email"]
    userText = request.args.get('msg', None)
    if userText:
        text = userText
    else:
        text = request.json['text']
    if not text:
        return 'false'
    tts = gTTS(text=text, lang='zh')
    file = BytesIO()
    tts.write_to_fp(file)
    file.seek(0)
    email_head = email.split('@')[0]
    text_head = text[0:20].replace(':', '').replace('/', '').replace('\n', '')
    fn = f"./audio/{email_head}-{text_head}-{str(uuid4()).replace('-', '')}.mp3"
    with open(fn, "wb") as f:
        f.write(file.read())
    logger.info(f'text to voice success:{fn} {text}')
    return send_file(fn, mimetype='audio/mpeg')


@api_voice.route('/api/transcription', methods=['POST', 'GET'])
def voice2text():
    # 获取录音文件
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({'transcription': 'No audio file provided.'})
    else:
        return jsonify({'transcription': 'No text'})
    # 语音识别
    client = speech.SpeechClient()
    audio = speech.types.RecognitionAudio(content=audio_file.read())
    config = speech.types.RecognitionConfig()
    response = client.recognize(config=config, audio=audio)

    # 获取转换结果
    results = [result.alternatives[0].transcript for result in response.results]
    transcription = " ".join(results)

    return jsonify({'transcription': transcription})


@api_voice.route("/voice")
def voice():
    if "email" in session:
        return render_template("voice.html")
    return redirect(url_for("login"))
