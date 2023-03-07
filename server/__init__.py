# -*- coding: utf-8 -*-
# @Project ：ChatGPT-Speech111
# @File ：__init__.py.py
# @Author ：XSM
# @Date ：2023/3/4 0:03
import logging

logger = logging.getLogger(name="crazyChat")
sh = logging.StreamHandler()
fh = logging.FileHandler("crazyChat.log")
fmt = '[%(asctime)s-%(name)s-%(levelname)s-%(filename)s-%(lineno)d]:%(message)s'
formatter = logging.Formatter(fmt=fmt)
sh.setFormatter(fmt=formatter)
fh.setFormatter(fmt=formatter)
logger.setLevel(level=logging.DEBUG)
# sh.setLevel(logging.DEBUG)
# fh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.addHandler(fh)
logger.info('初始化完成，日志打印正常！')
