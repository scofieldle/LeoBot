# -*- coding: UTF-8 -*-
import base64
import datetime
import functools
import hashlib
import inspect
import json
import os
import re
import time
from io import BytesIO
from pathlib import Path

import aiofiles
import yaml
from hoshino import CanceledException, aiorequests, priv, trigger
from nonebot import *
from PIL import ImageFont
from sqlitedict import SqliteDict

bot = get_bot()

try:
    import locale

    # 解决部分系统无法格式化中文时间问题
    locale.setlocale(locale.LC_CTYPE, 'chinese')
except Exception as e:
    pass

class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dict_obj):
    if not isinstance(dict_obj, dict):
        return dict_obj
    inst = Dict()
    for k, v in dict_obj.items():
        inst[k] = dict_to_object(v)
    return inst



# 格式化配置中的正则表达式
def format_reg(keyword, is_first=False):
    keyword = keyword if isinstance(keyword, list) else [keyword]
    return f"{'|'.join([f'^{i}' for i in keyword] if is_first else keyword)}"


def get_path(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)

def pil2b64(data):
    bio = BytesIO()
    data = data.convert("RGB")
    data.save(bio, format='JPEG', quality=75)
    base64_str = base64.b64encode(bio.getvalue()).decode()
    return 'base64://' + base64_str

db = {}


# 初始化数据库
def init_db(db_dir, db_name='db.sqlite', tablename='unnamed') -> SqliteDict:
    db_cache_key = db_name + tablename
    if db.get(db_cache_key):
        return db[db_cache_key]
    db[db_cache_key] = SqliteDict(get_path(db_dir, db_name),
                             tablename=tablename,
                             encode=json.dumps,
                             decode=json.loads,
                             autocommit=True)
    return db[db_cache_key]


# 寻找MessageSegment里的某个关键字的位置
def find_ms_str_index(ms, keyword, is_first=False):
    for index, item in enumerate(ms):
        if item['type'] == 'text' and re.search(format_reg(keyword, is_first),
                                                item['data']['text']):
            return index
    return -1


def filter_list(plist, func):
    return list(filter(func, plist))


def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def is_group_admin(ctx):
    return ctx['sender']['role'] in ['owner', 'admin', 'administrator']


def get_next_day():
    return time.mktime((datetime.date.today() +
                        datetime.timedelta(days=+1)).timetuple()) + 1000


def get_font(size, w='85'):
    return ImageFont.truetype(get_path('assets', 'font', f'HYWenHei {w}W.ttf'),
                              size=size)


def cache(ttl=datetime.timedelta(hours=1), **kwargs):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            bound = inspect.signature(func).bind(*args, **kw)
            bound.apply_defaults()
            ins_key = '|'.join(['%s_%s' % (k, v) for k, v in bound.arguments.items()])
            default_data = {"time": None, "value": None}
            data = cache_data.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data['time'] or now - data['time'] > ttl:
                try:
                    data['value'] = await func(*args, **kw)
                    data['time'] = now
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e

            return data['value']

        return wrapped

    return wrap

async def get_all_group():
    for self_id in bot._wsr_api_clients.keys():
        group = await bot.get_group_list(self_id=self_id)
        for group_info in group:
            yield group_info


async def get_group_info(group_id):
    async for group in get_all_group():
        if int(group_id) == group['group_id']:
            return dict_to_object(group)
