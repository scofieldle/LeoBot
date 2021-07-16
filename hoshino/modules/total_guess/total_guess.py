from hoshino.typing import CQEvent
from hoshino import Service
import math, sqlite3, os, random, asyncio

from PIL import Image
from io import BytesIO
import base64, codecs, json
from .guess import *

sv = Service('total', help_='猜一猜'.strip())

TEMP = {}
PREPARE_TIME = 5
ONE_TURN_TIME = 5

def get_question():
    #{'flag':True,'answer':[], 'img':'','game_type':'','question_list':[]}
    return random.choice([pcr_img_guess(),pcr_word_guess(),mrfz_img_guess(),mrfz_word_guess(),genshin_word_guess()])
    
def load_config():
    try:
        config_path = '/home/ubuntu/HoshinoBot/hoshino/modules/Genshin_wiki/Genshin_chara.json'
        with codecs.open(config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except Exception as e:
        sv.logger.info(e)
        return {}

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
        pass

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
        pass

@sv.on_fullmatch('猜一猜')
async def guess(bot, ev: CQEvent):
    global TEMP
    gid = ev.group_id
    try:
        if not gid in TEMP.keys():
            TEMP[gid] = {'flag':True,'answer':[], 'img':'','game_type':'','question_list':[]}
        elif TEMP[gid]['flag']:
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        
        TEMP[gid] = get_question()
        if TEMP[gid]['game_type'] == 'word':
            await bot.send(ev, f'{PREPARE_TIME}秒钟后每隔{ONE_TURN_TIME}秒我会给出某位角色的一个描述，根据这些描述猜猜她/他是谁~')
            await asyncio.sleep(PREPARE_TIME)
        
            for question in TEMP[gid]['question_list']:
                if not TEMP[gid]['flag']:
                    return
                await bot.send(ev, question)
                await asyncio.sleep(ONE_TURN_TIME)
                
        else:
            await bot.send(ev, TEMP[gid]['question_list'])
            await asyncio.sleep(20)
            if not TEMP[gid]['flag']:
                return
            
        msg_part = '很遗憾，没有人答对~'
        msg =  f'正确答案是: {TEMP[gid]["answer"][0]}{TEMP[gid]["img"]}\n{msg_part}'
        await bot.send(ev, msg)
        TEMP[gid]['flag'] = False
    except Exception as e:
        print(e)
        TEMP[gid]['flag'] = False
        
@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    global TEMP
    try:
        s = ev.message.extract_plain_text()
        gid = ev.group_id
        if gid in TEMP.keys() and TEMP[gid]['flag']:
            if s in TEMP[gid]['answer']:
                msg_part = f'猜对了，真厉害!\n(此轮游戏将在几秒后自动结束，请耐心等待)'
                msg =  f'正确答案是: {TEMP[gid]["answer"][0]}{TEMP[gid]["img"]}\n{msg_part}'
                await bot.send(ev, msg, at_sender=True)
                TEMP[gid]['flag'] = False
    except Exception as e:
        print(e)
        TEMP[gid]['flag'] = False
