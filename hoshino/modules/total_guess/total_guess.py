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
weapon_path = config_path = os.path.join(os.path.dirname(__file__), 'weapon_info')
character_path = config_path = os.path.join(os.path.dirname(__file__), 'character_info')

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

@sv.on_prefix(('来点'))
async def Genshin_wiki(bot, ev: CQEvent):
    try:
        chara_list = load_config('Genshin_chara.json')
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
      
@sv.on_fullmatch(('全部原神武器','全部原神角色'))
async def total_ys(bot, ev: CQEvent):
    info = ev.raw_message
    if info.endswith('武器'):
        weapon_list = os.listdir(weapon_path)
        msg = '请使用命令 [查看原神武器 武器名字]'
        for item in weapon_list:
            msg += '\n'
            msg += item.replace('.png','')
        msg = [{"type": "node","data": {"name": "小冰","uin": "2854196306","content":msg}}]
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
        return
    if info.endswith('角色'):
        chara_list = os.listdir(character_path)
        msg = '请使用命令 [查看原神角色 角色名字]'
        for item in chara_list:
            msg += '\n'
            msg += item.replace('.png','')
        msg = [{"type": "node","data": {"name": "小冰","uin": "2854196306","content":msg}}]
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
        return

@sv.on_prefix('查看原神武器')
async def ys_weapon(bot, ev: CQEvent):
    s = ev.message.extract_plain_text() + '.png'
    weapon_list = os.listdir(weapon_path)
    if s in weapon_list:
        img = Image.open(os.path.join(weapon_path, s))
        image = MessageSegment.image(pic2b64(img))
        msg = [{"type": "node","data": {"name": "小冰","uin": "2854196306","content":image}}]
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
    else:
        await bot.send(ev, f'没有叫{ev.message}的武器哦！')

@sv.on_prefix('查看原神角色')
async def ys_character(bot, ev: CQEvent):
    s = ev.message.extract_plain_text()
    chara_name = load_config('character.json')
    if not s:
        return
    for key,value in chara_name.items():
        if s in value or s == key:
            s = key + '.png'
            img = Image.open(os.path.join(character_path, s))
            image = MessageSegment.image(pic2b64(img))
            msg = [{"type": "node","data": {"name": "小冰","uin": "2854196306","content":image}}]
            await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
            return
    await bot.send(ev, f'没有叫{ev.message}的角色哦！')

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
