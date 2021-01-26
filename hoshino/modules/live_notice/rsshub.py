# -*- coding: UTF-8 -*-
import asyncio
import json
import os
import re
from io import BytesIO
import numpy as np
import codecs
import feedparser
import requests
from nonebot.log import logger
from .config import *

# 存储目录
file_path = abs_path

async def getRSS(rss):  # 链接，订阅名
    d = ""
    try:
        old = readRss(rss)
        r = await requests.get(rss.geturl(rss.platform), timeout=30)
        d = feedparser.parse(r.content)
    except:
        logger.error("抓取订阅 {} 的 RSS 失败".format(rss.geturl(rss.platform)))
        return False

    # 检查是否存在rss记录
    if d['entries'] == []:
        return False
    else:
        pubdate = d['entries'][0]['published']
        if pubdate == old:
            return False
        else:
            writeRss(rss, pubdate)
            return True

# 读取记录
def readRss(rss):
    file = file_path + rss.platform + rss.url + ".json"
    try:
        if os.path.exists(file):
            with codecs.open(file, 'r', encoding='utf-8') as load_f:
                load_dict = json.load(load_f)
            return load_dict
        else:
            with codecs.open(file, 'w', encoding='utf-8') as f:
                f.write('0')
            return ''
    except:
        logger.info('打开文件失败：' + rss.url)
        return ''
    

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
            
# 写入记录
def writeRss(rss, msg):
    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    try:
        with codecs.open(file_path + rss.platform + rss.url + ".json", 'w', encoding='utf-8') as dump_f:
            dump_f.write(json.dumps(msg, sort_keys=True, indent=4, cls=MyEncoder))
    except:
        logger.info('写入文件失败：' + rss.url)
