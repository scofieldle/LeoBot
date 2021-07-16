import json
import asyncio
import copy
import nonebot
import hoshino
from os import path
from hoshino import Service, priv, aiorequests
from datetime import datetime

sv1 = Service('车站查询', enable_on_default=True)
sv2 = Service('车站推送', enable_on_default=False)

config = {}
config_path = path.join(path.dirname(__file__), "config.json")
with open(config_path, "r", encoding="utf8")as fp:
    config = json.load(fp)


def load_config():
    global config
    config_path = path.join(path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf8")as fp:
        config = json.load(fp)


def save_config():
    config_path = path.join(path.dirname(__file__), "config.json")
    jsonStr = json.dumps(config, indent=4)
    with open(config_path, "r+", encoding="utf8")as fp:
        fp.truncate(0)
        fp.seek(0)
        fp.write(jsonStr)   


@sv1.on_fullmatch('查询车站人数')
async def query_number(bot, ev):
    resp = json.loads((await (await aiorequests.get('https://api.bandoristation.com/?function=get_online_number')).content).decode('utf8'))
    status = resp['status']
    if status == 'failure':
        sv1.logger.info('Api出错，请停用插件')
        await bot.finish(ev, '查询失败，请联系维护.', at_sender=True)
    else:
        res = resp['response']
        num = res['online_number']
        await bot.send(ev, f'车站目前有{num}人停留.')


@sv1.on_fullmatch(('ycm', '有车吗'))
async def query_room(bot, ev):
    resp = json.loads((await (await aiorequests.get('https://api.bandoristation.com/?function=query_room_number')).content).decode('utf8'))
    status = resp['status']
    if status == 'failure':
        sv1.logger.info('Api出错，请停用插件')
        await bot.finish(ev, '查询失败，请联系维护.', at_sender=True)
    else:
        res = resp['response']
        if not res:
            await bot.finish(ev, '目前没有等待中的房间，请稍后查询.', at_sender=True)
        else:
            room = res[0]['number']
            putline = []
            if room:
                room = res[0]['number']
                raw_message = res[0]['raw_message']
                room_type = res[0]['type']
                if room_type == '25':
                    room_type = '25w room'
                elif room_type == '7':
                    room_type = '7w room'
                elif room_type == '12':
                    room_type = '12w room'
                elif room_type == '18':
                    room_type = '18w room'
                else:
                    room_type = 'Free room'
                time = datetime.fromtimestamp(res[0]['time'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                user_id = res[0]['user_info']['user_id']
                username = res[0]['user_info']['username']
                name = res[0]['source_info']['name']
                source_type = res[0]['source_info']['type']
                putline.append('--房间信息--')
                putline.append('房间号：{}'.format(room))
                putline.append('房间类型：{}'.format(room_type))
                putline.append('发布时间：{}'.format(time))
                putline.append('发布用户：{}({})'.format(username, user_id))
                putline.append('发布来源：{}({})'.format(name, source_type))
                putline.append('房间说明：{}'.format(raw_message))
            result = "\n".join(putline)
            await bot.send(ev, result)


@sv2.on_prefix('开启车站通知')
async def add_group(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '请联系群管理为本群开启车站通知.', at_sender=True)
    gid = str(ev.group_id)
    if not gid in config['station_notice']:
        config['station_notice'][gid] = {"gid":gid, "notice_on":True}
    else:
        await bot.finish(ev, '本群已经开启车站通知了.', at_sender=True)
    save_config()
    await bot.send(ev, '开启成功', at_sender=True)


@sv2.on_prefix('关闭车站通知')
async def delete_group(bot, ev):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '请联系群管理为本群关闭车站通知.', at_sender=True)
    gid = str(ev.group_id)
    if not gid in config['station_notice']:
        await bot.finish(ev, '本群还没有开启车站通知.', at_sender=True)
    else:
        config['station_notice'][gid]['notice_on'] = False
        save_config()
        await bot.send(ev, '关闭成功', at_sender=True)


@sv2.scheduled_job('interval', minutes=2)
async def query_schedule():
    bot = nonebot.get_bot()
    weihu = hoshino.config.SUPERUSERS[0]
    resp = json.loads((await (await aiorequests.get('https://api.bandoristation.com/?function=query_room_number')).content).decode('utf8'))
    status = resp['status']
    if status == 'failure':
        sv2.logger.info('Api出错，请停用插件')
        warn = 'BandoriStation api出错，请停用插件'
        await bot.send_private_msg(user_id=weihu, message=warn)
    else:
        res = resp['response']
        if not res:
            pass
        else:
            room = res[0]['number']
            putline = []
            if room:
                room = res[0]['number']
                raw_message = res[0]['raw_message']
                room_type = res[0]['type']
                if room_type == '25':
                    room_type = '25w room'
                elif room_type == '7':
                    room_type = '7w room'
                elif room_type == '12':
                    room_type = '12w room'
                elif room_type == '18':
                    room_type = '18w room'
                else:
                    room_type = 'Free room'
                time = datetime.fromtimestamp(res[0]['time'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                user_id = res[0]['user_info']['user_id']
                username = res[0]['user_info']['username']
                name = res[0]['source_info']['name']
                source_type = res[0]['source_info']['type']
                putline.append('--房间信息--')
                putline.append('房间号：{}'.format(room))
                putline.append('房间类型：{}'.format(room_type))
                putline.append('发布时间：{}'.format(time))
                putline.append('发布用户：{}({})'.format(username, user_id))
                putline.append('发布来源：{}({})'.format(name, source_type))
                putline.append('房间说明：{}'.format(raw_message))
            msg = "\n".join(putline)
            station_notice = copy.deepcopy(config['station_notice'])
            for gid in station_notice:
                gid = str(gid)
                await asyncio.sleep(1.5)
                if config['station_notice'][gid]['notice_on']:
                    await bot.send_group_msg(group_id=int(config['station_notice'][gid]['gid']), message=msg)
                    await asyncio.sleep(1.5)