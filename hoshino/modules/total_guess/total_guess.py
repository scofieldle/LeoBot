from hoshino.typing import CQEvent
from hoshino import Service
import random, asyncio
import codecs, json
from hoshino.util import pic2b64
from PIL import Image
from nonebot import MessageSegment
from .guess import *

sv = Service('total', help_='猜一猜'.strip())

TEMP = {}
PREPARE_TIME = 5
ONE_TURN_TIME = 5

def get_question(signal):
    if signal == '猜干员' or signal == '猜明日方舟':
        return random.choice([mrfz_img_guess(),mrfz_word_guess()])
    if signal == '猜原神':
        return genshin_word_guess()
    if signal == '猜角色' or signal == '猜pcr' or signal == '猜公主连结':
        return random.choice([pcr_img_guess(),pcr_word_guess()])
    return random.choice([pcr_img_guess(),pcr_word_guess(),mrfz_img_guess(),mrfz_word_guess(),genshin_word_guess()])
    
def load_config(json_name):
    try:
        config_path = os.path.join(os.path.dirname(__file__), json_name)
        with codecs.open(config_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except Exception as e:
        sv.logger.info(e)
        return {}

@sv.on_fullmatch(('猜一猜','猜干员','猜明日方舟','猜角色','猜原神','猜pcr','猜公主连结'))
async def guess(bot, ev: CQEvent):
    global TEMP
    gid = ev.group_id
    signal = ev.raw_message
    try:
        if not gid in TEMP.keys():
            TEMP[gid] = {'flag':True,'answer':[], 'img':'','game_type':'','question_list':[]}
        elif TEMP[gid]['flag']:
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        
        TEMP[gid] = get_question(signal)
        if TEMP[gid]['game_type'] == 'word':
            await bot.send(ev, f'{PREPARE_TIME}秒钟后每隔{ONE_TURN_TIME}秒我会给出某位角色的一个描述，根据这些描述猜猜她/他是谁~')
            await asyncio.sleep(PREPARE_TIME)
        
            for question in TEMP[gid]['question_list']:
                if not TEMP[gid]['flag']:
                    return
                await bot.send(ev, question)
                await asyncio.sleep(ONE_TURN_TIME)
                if not TEMP[gid]['flag']:
                    return
                
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
        TEMP[gid] = {'flag':False,'answer':[], 'img':'','game_type':'','question_list':[]}
        await bot.send(ev, "遇到错误数据",at_sender=True)

@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    global TEMP
    try:
        s = ev.message.extract_plain_text()
        gid = ev.group_id
        if gid in TEMP.keys() and TEMP[gid]['flag']:
            if s in TEMP[gid]['answer']:
                msg_part = f'猜对了，真厉害!\n(此轮游戏将在几秒后自动结束，请耐心等待)'
                msg =  f'正确答案是: {random.choice(TEMP[gid]["answer"])}{TEMP[gid]["img"]}\n{msg_part}'
                await bot.send(ev, msg, at_sender=True)
                TEMP[gid]['flag'] = False
    except Exception as e:
        print(e)
        TEMP[gid]['flag'] = False
