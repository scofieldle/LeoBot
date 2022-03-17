from hoshino.typing import CQEvent
from hoshino import Service
import random, os
import codecs, json
from hoshino.util import pic2b64
from PIL import Image
from nonebot import MessageSegment

sv = Service('genshin_info')
weapon_path = config_path = os.path.join(os.path.dirname(__file__), 'weapon_info')
character_path = config_path = os.path.join(os.path.dirname(__file__), 'character_info')

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
        chara_name = load_config('char_name.json')
        s = ev.message.extract_plain_text()
        name = s
        if '故事' in name or '语音' in name or '技能' in name:
            tag = name[-2:]
            name = name[:-2].replace(' ','')
            for temp in chara_name.keys():
                if name in chara_name[temp]:
                    name = temp
                    break
            if name in chara_list.keys() and tag in chara_list[name].keys():
                index_list = chara_list[name][tag]
                random.shuffle(index_list)
                msg = index_list[0][0] + ':' + index_list[0][1]
                await bot.send(ev, msg, at_sender=True)
            else:
                await bot.send(ev, f'{name}缺少{tag}，请提醒管理员补充数据')
        elif '命之座' in name:
            tag = name[-3:]
            name = name[:-3].replace(' ','')
            for temp in chara_name.keys():
                if name in chara_name[temp]:
                    name = temp
                    break
            if name in chara_list.keys() and tag in chara_list[name].keys():
                index_list = chara_list[name][tag]
                random.shuffle(index_list)
                msg = index_list[0][0] + ':' + index_list[0][1]
                await bot.send(ev, msg, at_sender=True)
            else:
                await bot.send(ev, f'{name}缺少{tag}，请提醒管理员补充数据')
        else:
            for temp in chara_name.keys():
                if name in chara_name[temp]:
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

@sv.on_prefix(('查看技能','查看故事','查看语音','查看命之座'))
async def Genshin_wiki(bot, ev: CQEvent):
    chara_list = load_config('Genshin_chara.json')
    chara_name = load_config('char_name.json')
    name = ev.message.extract_plain_text()

    info = ev.raw_message
    info = info.replace(name,'')
    info = info.replace('查看','')
    info = info.replace(' ','')

    for temp in chara_name.keys():
        if name in chara_name[temp]:
            name = temp
            break
    if name in chara_list.keys() and info in chara_list[name].keys():
        index_list = chara_list[name][info]
        msg = []
        for i in index_list:
            if len(i[1]) > 150:
                msg.append({"type": "node","data": {"name": "bot","uin": "197812783","content":i[0]+':'+i[1][:150]}})
                msg.append({"type": "node","data": {"name": "bot","uin": "197812783","content":i[0]+':'+i[1][150:]}})
            else:
                msg.append({"type": "node","data": {"name": "bot","uin": "197812783","content":i[0]+':'+i[1]}})
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)

@sv.on_fullmatch(('全部原神武器','全部原神角色','查看全部原神武器','查看全部原神角色'))
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

def check(s,weapon):
    weapon = weapon.split('.')[0]
    temp = 0
    num = 1.0/len(weapon)
    for i in weapon:
        if i in s:
            temp += num
    return int(100*temp)

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
        for weapon in weapon_list:
            temp = check(s,weapon) 
            if temp > 50:
                img = Image.open(os.path.join(weapon_path, weapon))
                image = MessageSegment.image(pic2b64(img))
                msg = [{"type": "node","data": {"name": "小冰","uin": "2854196306","content":image}}]
                await bot.send(ev,f'您有{temp}%的可能在找{weapon}')
                await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
                return
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