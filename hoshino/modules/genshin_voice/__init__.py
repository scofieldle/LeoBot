import json
import os
import random, asyncio
from typing import Optional, Tuple
from . import update
from hoshino import Service
from nonebot import MessageSegment
from PIL import Image
from hoshino.util import pic2b64

language_mapping = {'cn':['中','中国','汉语','中文','中国话','Chinese','cn'], 'jp':['日','日本','日语','霓虹','日本语','Japanese','jp'], 
            'en':['英','英文','英语','洋文','English','en'], 'kr':['韩','韩国','韩语','棒子','南朝鲜','南朝鲜语','kr']}

try:
    with open(os.path.join(os.path.dirname(__file__), 'char_name.json'), 'r', encoding='utf8') as f:
        char_name = json.load(f)
    with open(os.path.join(os.path.dirname(__file__), 'char_voice.json'), 'r', encoding='utf8') as f:
        char_voice = json.load(f)
except Exception as e:
    print("loading file failed:", e)

def name_zh2en(name: str) -> Tuple[str, bool]:
    for k, v in char_name.items():
        if name in v:
            return k, True
    return char_name["unknown"][0], False

def get_random_voice(name, language: Optional[str] = 'cn') -> Optional[str]:
    if name:
        characters = name_zh2en(name)
        if not characters[1]:
            return None
        characters = characters[0]
        voice = None
        while not voice:
            action = random.choice(list(char_voice[characters].keys()))
            if language in char_voice[characters][action].keys():
                voice = char_voice[characters][action][language]
            else:
                continue
        return voice
    else:
        return None

def get_cqcode(name):
    pic_name = name + '.jpg'
    parent = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent,'total_guess','pic',pic_name)
    img = Image.open(path)
    image = MessageSegment.image(pic2b64(img))
    return str(image)

def get_question(lan):
    answer = random.choice(list(char_name.keys()))
    img = get_cqcode(char_name[answer][0])
    question = get_random_voice(char_name[answer][0], lan)
    return {'flag':True,'answer':char_name[answer], 'img':img,'question':question}

_help = """
[原神猜语音]
[原神语音 (角色名) (语言)] 播放一段角色的语音(不加语言默认中文)
[更新原神语音列表] 从资源站上更新语音列表
"""

sv = Service('原神语音', help_=_help)
#f'[CQ:record,file={voice}]'
TEMP = {}

@sv.on_prefix('原神语音')
async def get_genshin_voice(bot, ev):
    name = ev.message.extract_plain_text().split(" ")
    try:
        for k, v in language_mapping.items():
            if name[1] in v:
                lan = k
    except:
        lan = 'cn'
    path = get_random_voice(name[0], lan)
    if not path:
        await bot.send(ev, f'没有找到{name[0]}的语音呢')
    await bot.send(ev, f'[CQ:record,file={path}]')

@sv.on_prefix(('原神猜语音','猜原神语音'))
async def guess_genshin_voice(bot, ev):
    global TEMP
    keyword = ev.message.extract_plain_text()
    gid = ev.group_id
    if keyword:
        for k, v in language_mapping.items():
            if keyword in v:
                lan = k
    else:
        lan = random.choice(['cn','jp','kr','en'])
    
    try:
        if not gid in TEMP.keys():
            TEMP[gid] = {'flag':True,'answer':'', 'img':'','question':''}
        elif TEMP[gid]['flag']:
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        TEMP[gid] = get_question(lan)
        answer = TEMP[gid]['answer'][0]
        await bot.send(ev, f'即将发送一段原神语音,将在20秒后公布答案')
        await bot.send(ev, f'[CQ:record,file={TEMP[gid]["question"]}]')
        await asyncio.sleep(20)
        if not TEMP[gid]['flag'] or answer != TEMP[gid]['answer'][0]:
            return
        else:
            msg_part = '很遗憾，没有人答对~'
            msg =  f'正确答案是: {TEMP[gid]["answer"][0]}\n{TEMP[gid]["img"]}\n{msg_part}'
            await bot.send(ev, msg)
            TEMP[gid]['flag'] = False
    except Exception as e:
        print(e)
        TEMP[gid]['flag'] = False

@sv.on_message()
async def on_input_chara_name(bot, ev):
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

@sv.on_fullmatch("更新原神语音列表")
async def update_voices(bot, ev):
    await bot.send(ev, "开始更新...")
    update.main()
    await bot.send(ev, "更新完成")
