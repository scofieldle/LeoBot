import os
import json
import traceback
import asyncio
import aiohttp
import random
import string
import base64
from hoshino import R
from .config import get_config, get_group_config
from .lolicon import lolicon_init, lolicon_get_setu,lolicon_fetch_process, lolicon_search_setu


def check_path():
    state = {}
    sub_dirs = ['lolicon', 'lolicon_r18']
    for item in sub_dirs:
        res = './res/img/setu_mix/' + item
        if not os.path.exists(res):
            os.makedirs(res)
        state[item] = len(os.listdir(res)) // 2
    return state
check_path()

def add_salt(data):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    return data + bytes(salt, encoding="utf8")

def format_setu_msg(image):
    base64_str = f"base64://{base64.b64encode(add_salt(image['data'])).decode()}"
    msg = f'title:{image["title"]}\nauthor:{image["author"]}\nid:{image["id"]}\n[CQ:image,file={base64_str}]'
    return msg

async def get_setu(group_id):
    source_list = []
    if get_group_config(group_id, 'lolicon'):
        source_list.append(1)
    if get_group_config(group_id, 'lolicon_r18'):
        source_list.append(2)
    source = 0
    if len(source_list) > 0:
        source = random.choice(source_list)
    
    image = None
    if source == 1:
        image = await lolicon_get_setu(0)
    elif source == 2:
        image = await lolicon_get_setu(1)
    else:
        return None
    if not image:
        return '获取失败'
    elif image['id'] != 0:
        return format_setu_msg(image)
    else:
        return image['title']

async def search_setu(group_id, keyword, num):
    source_list = []
    if get_group_config(group_id, 'lolicon') and get_group_config(group_id, 'lolicon_r18'):
        source_list.append(2)
    elif get_group_config(group_id, 'lolicon'):
        source_list.append(0)
    elif get_group_config(group_id, 'lolicon_r18'):
        source_list.append(1)

    if len(source_list) == 0:
        return None
    
    image_list = None
    msg_list = []
    while len(source_list) > 0 and len(msg_list) == 0:
        source = source_list.pop(random.randint(0, len(source_list) - 1))
        if source == 0:
            image_list = await lolicon_search_setu(keyword, 0, num)
        elif source == 1:
            image_list = await lolicon_search_setu(keyword, 1, num)
        elif source == 2:
            image_list = await lolicon_search_setu(keyword, 2, num)
        if image_list and len(image_list) > 0:
            for image in image_list:
                msg_list.append(format_setu_msg(image))
    return msg_list

async def fetch_process():
    tasks = []
    tasks.append(asyncio.ensure_future(lolicon_fetch_process()))
    for task in asyncio.as_completed(tasks):
        await task

lolicon_init()