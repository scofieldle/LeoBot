import os
import json
import traceback
import aiohttp
import io
import random
import datetime
from PIL import Image
from hoshino import R
from .config import get_config
from pixivpy3 import *

quota_limit_time = datetime.datetime.now()
api = AppPixivAPI()
try:
    api.auth(refresh_token=get_config('pixiv','token'))
except:
    pass

def generate_image_struct():
    return {
        'id': 0,
        'url': '',
        'title': '',
        'author_id': 0,
        'author': '',
        'tags': [],
        'date': '',
        'bookmarks': 0,
    }

native_info = []

def load_native_info():
    info = []
    res = './res/img/pixiv/'
    if not os.path.exists(res):
        return info
    pic_list =  os.listdir(res)

    for pic in pic_list:
        uid = int(pic.split('.')[0])
        info.append(uid)
    return info

def init_image(illust):
    image = generate_image_struct()
    image['id'] = illust['id']
    image['title'] = illust['title']
    image['url'] = illust['image_urls']['large']
    image['author'] = illust['user']['name']
    image['author_id'] = illust['user']['id']
    image['date'] = illust['create_date'].split('T')[0]
    image['bookmarks'] = illust['total_bookmarks']
    for tag in illust['tags']:
        image['tags'].append(tag['name'])
    return image

async def download_image(url: str, id: int):
    global api
    res = './res/img/pixiv/'
    try:
        api.download(url, path = res, name = str(id) + '.jpg')
    except:
        print('download image failed')

async def query_keyword(keyword):
    global quota_limit_time, api
    image_list = []
    if datetime.datetime.now() < quota_limit_time:
        return image_list
    
    try:
        json_result = api.search_illust(keyword, search_target='partial_match_for_tags')
        love = 0
        illust = ''
        for temp in json_result.illusts:
            new_love = api.illust_detail(temp.id)['illust']['total_bookmarks']
            if new_love > love:
                illust = temp
                love = new_love
    except Exception:
        traceback.print_exc()
        return image_list
    quota_limit_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
    image_list.append(init_image(illust))
    return image_list

async def query_(keyword, uid = 0, r18 = 0):
    global quota_limit_time, api
    image_list = []
    if datetime.datetime.now() < quota_limit_time:
        return image_list
    
    try:
        if '画师' in keyword:
            json_result = api.user_illusts(uid)['illusts'][:10]
        elif '日榜' in keyword:
            if r18:
                json_result = api.illust_ranking(mode='day_r18')['illusts'][:15]
            else:
                json_result = api.illust_ranking(mode='day')['illusts'][:15]
        elif '周榜' in keyword:
            if r18:
                json_result = api.illust_ranking(mode='week_r18')['illusts'][:15]
            else:
                json_result = api.illust_ranking(mode='week')['illusts'][:15]
        elif '月榜' in keyword:
            json_result = api.illust_ranking(mode='month')['illusts'][:15]
        else:
            json_result = api.illust_related(uid)['illusts'][:10]
    except:
        json_result = 0
    
    if not json_result:
        try:
            api = AppPixivAPI()
            await api.auth(refresh_token=get_config('pixiv','token'))
        except:
            pass
        return image_list
    
    quota_limit_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
    for item in json_result:
        image_list.append(init_image(item))
    return image_list

def native_get(uid):
    global native_info
    if uid in native_info:
        return True
    else:
        return False

def pixiv_init():
    global native_info
    native_info = load_native_info()
