from hoshino import Service
from hoshino.typing import CQEvent
from .config import *

import math, sqlite3, os, random, asyncio, hoshino, json, codecs
from nonebot import MessageSegment
from hoshino.util import pic2b64
from PIL import Image

sv = Service('genshin_guess', bundle='原神猜角色', help_='''
猜原神
来点xx[故事，语音]， []中不写会随机发送
查看xx命之座
'''.strip())

def load_config():
    try:
        config_path = hoshino_path + 'Genshin_chara.json'
        with codecs.open(config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except Exception as e:
        sv.logger.info(e)
        return {}

TEMP = {}
PREPARE_TIME = 5
ONE_TURN_TIME = 8
TURN_NUMBER = 5

    
def get_cqcode(gid):
    global TEMP
    dir_path = img_path + TEMP[gid]['answer'] + '.png'
    img = Image.open(dir_path)
    image = MessageSegment.image(pic2b64(img))
    return image

@sv.on_prefix(('来点'))
async def Genshin_wiki(bot, ev: CQEvent):
    try:
        chara_list = load_config()
        s = ev.message.extract_plain_text()
        name = s
        if '故事' in name or '语音' in name:
            tag = name[-2:]
            name = name[:-2].replace(' ','')
            for temp in chara_list.keys():
                if name in temp:
                    name = temp
                    break
            if tag in chara_list[name].keys() and name in chara_list.keys():
                index_list = chara_list[name][tag]
                random.shuffle(index_list)
                msg = index_list[0][0] + ':' + index_list[0][1]
                await bot.send(ev, msg, at_sender=True)
            else:
                await bot.send(ev, f'{name}缺少{tag}，请提醒管理员补充数据')
        else:
            for temp in chara_list.keys():
                if name in temp:
                    name = temp
                    break
            if name in chara_list.keys():
                tag_label = list(chara_list[name].keys())
                random.shuffle(tag_label)
                index_list = chara_list[name][tag_label[0]]
                random.shuffle(index_list)
                msg = index_list[0][0] + ':' + index_list[0][1]
                await bot.send(ev, msg, at_sender=True)
            else:
                return
    except Exception as e:
        sv.logger.info(e)

@sv.on_suffix(('命之座'))
async def Genshin_MZZ(bot, ev: CQEvent):
    try:
        s = ev.message.extract_plain_text()
        sv.logger.info(s)
        if '查看' in s:
            chara_list = load_config()
            name = s[2:].replace(' ','')
            for temp in chara_list.keys():
                if name in temp:
                    name = temp
                    break
            if name in chara_list.keys():
                index_list = chara_list[name]['命之座']
                msg = ''
                for item in index_list:
                    msg = msg + item[0] + ':' + '\n' + item[1] + '\n'
                await bot.send(ev, msg)
            else:
                await bot.send(ev, f'没有叫{name}的人哦！', at_sender=True)
    except Exception as e:
        sv.logger.info(e)

@sv.on_fullmatch(('猜原神'))
async def description_guess(bot, ev: CQEvent):
    global TEMP
    gid = ev.group_id
    try:
        if not gid in TEMP.keys():
            TEMP[gid] = {'flag':False,'answer':''}
        if TEMP[gid]['flag']:
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        await bot.send(ev, f'{PREPARE_TIME}秒钟后每隔{ONE_TURN_TIME}秒我会给出某位角色的一个描述，根据这些描述猜猜她是谁~')
        await asyncio.sleep(PREPARE_TIME)
        
        chara_list = load_config()
        chara_name_list = list(chara_list.keys())
        random.shuffle(chara_name_list)
        TEMP[gid]['answer'] = chara_name_list[0]
        answer = chara_name_list[0]
        data_label = list(chara_list[answer].keys())
        data_label.remove('故事')
        for i in range(TURN_NUMBER):
            random.shuffle(data_label)
            index_list = chara_list[answer][data_label[0]]
            random.shuffle(index_list)
            if data_label[0] == '命之座':
                await bot.send(ev, f'提示{i+1}/{TURN_NUMBER}:\n{data_label[0]}有 {index_list[0][0]}')
                del(chara_list[answer][data_label[0]][0])
                await asyncio.sleep(ONE_TURN_TIME)
            else:
                await bot.send(ev, f'提示{i+1}/{TURN_NUMBER}:\n{data_label[0]}有 {index_list[0][1]}')
                del(chara_list[answer][data_label[0]][0])
                await asyncio.sleep(ONE_TURN_TIME)
            if not TEMP[gid]['flag']:
                return
        msg_part = '很遗憾，没有人答对~'
        img = get_cqcode(gid)
        msg =  f'正确答案是: {answer}{img}\n{msg_part}'
        await bot.send(ev, msg)
    except Exception as e:
        sv.logger.info(e)


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    global TEMP
    try:
        s = ev.message.extract_plain_text()
        gid = ev.group_id
        answer = TEMP[gid]['answer']
        if TEMP[gid]['flag'] and s in answer:
            img = get_cqcode(gid)
            msg_part = f'猜对了，真厉害!\n(此轮游戏将在几秒后自动结束，请耐心等待)'
            msg =  f'正确答案是: {answer}{img}\n{msg_part}'
            await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        sv.logger.info(e)
