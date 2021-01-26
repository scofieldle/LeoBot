import re, hoshino, os, json

from . import RSS_class, rsshub
from hoshino import Service, priv
from hoshino.typing import CQEvent
from .config import *

sv = Service('live_spider', bundle='live订阅', help_='''
添加直播订阅 直播平台 订阅名 直播id
删除直播订阅 订阅名
查看直播订阅
'''.strip())

platform_list = ['bilibili','斗鱼']

def load_config(platform):
    if platform == '斗鱼':
        config_path = hoshino_path + '斗鱼_config.json'
    if platform == 'bilibili':
        config_path = hoshino_path + 'bilibili_config.json'
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf8') as config_file:
                return json.load(config_file)
        else:
            return {}
    except:
        return {}

def save_config(platform, config):
    try:
        with open(hoshino_path + platform +'_config.json', 'w', encoding='utf8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
        return True
    except:
        return False


async def spider_work(rss, bot, sv:Service):
    update = await rsshub.getRSS(rss)
    if not update:
        sv.logger.info(f'{rss.platform}{rss.url}未开启直播')
        return
    sv.logger.info(f'{rss.platform}{rss.url}开启直播了！')
    await bot.send_group_msg(f'{rss.platform}{rss.url}开启直播了！')
            

@sv.on_prefix('添加直播订阅')
async def handle_RssAdd(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    s = ev.message.extract_plain_text().split(' ')
    try:
        platform = s[0]
        name = s[1]
        url = s[2]
    except:
        await bot.send(ev, '请输入：添加直播订阅 直播平台 昵称 直播id')
        return

    config = load_config(platform)
    gid = str(ev.group_id)
    if url in config.keys():
        gidList = []
        for item in config[url]:
            gidList.append(item[0])
        if gid not in gidList:
            config[url].append([gid,name])
        else:
            await bot.finish(ev, '此群已经添加过该订阅，请勿重复添加')
    else:
        config[url] = []
        config[url].append([gid,name])
    
    if save_config(platform, config):
        await bot.send(ev, f'添加订阅"{s}"成功!')
        # 重新加载缓存
        await live_search_spider()
    else:
        await bot.send(ev, '添加订阅失败，请重试')


@sv.on_prefix('删除直播订阅')
async def handle_RssDel(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')

    s = ev.message.extract_plain_text().split(' ')
    try:
        platform = s[0]
        name = s[1]
    except:
        await bot.send(ev, '请输入：删除直播订阅 直播平台 昵称')
        return
    config = load_config(platform)
    gid = str(ev.group_id)
    for url in config.keys():
        for item in config[url]:
            if item[0] == gid and name == item[1]:
                config[url].remove(item)
                msg = f'删除订阅"{name}"成功'
                if not save_config(platform, config):
                    await bot.finish(ev, '删除订阅失败，请重试')
                await bot.send(ev, msg)
                return
    msg = f'删除失败, 此群未设置订阅"{name}"'
    await bot.send(ev, msg)
    

@sv.on_fullmatch('查看直播订阅')
async def handle_RssLook(bot, ev: CQEvent):
    s = ev.message.extract_plain_text().split(' ')
    try:
        platform = s[0]
    except:
        await bot.send(ev, '请输入：查看直播订阅 直播平台')
        return
    config = load_config(platform)
    gid = str(ev.group_id)
    msg = '' 
    for url in config.keys():
        for item in config[url]:
            if item[0] == gid:
                msg = msg + '\n' + item[1] + ': ' + url
    if msg == '':
        msg = '此群还未添加直播订阅'
    else:
        msg = '直播订阅已开启!\n此群设置的订阅为:'  + msg
    await bot.send(ev, msg)

@sv.scheduled_job('interval',minutes=2)
async def live_search_spider():
    bot = hoshino.get_bot()
    for platform in platform_list:
        config = load_config(platform)
        for url in config.keys():
            gid = []
            for item in config[url]:
                gid.append(item[0])
            if gid:
                rss = RSS_class.rss()
                rss.platform = platform
                rss.url = url
                rss.gid = gid
                await spider_work(rss, bot, sv)
    