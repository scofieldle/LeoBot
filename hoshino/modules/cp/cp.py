# -*- coding: utf-8 -*-
import ujson
import os
import random
import aiofiles
from hoshino import Service

sv = Service('cp', bundle='cp小故事', help_='''
cp 攻 受
'''.strip())

path = '/home/ubuntu/HoshinoBot/hoshino/modules/cp'

def readInfo(file):
    with open(os.path.join(path,file), 'r', encoding='utf-8') as f:
        return ujson.loads((f.read()).strip())
    raise Exception

def getMessage(bot, userGroup):
    content = readInfo('content.json')
    content = random.choice(content['data']).replace('<攻>', userGroup[0]).replace('<受>', userGroup[1])
    return content

@sv.on_prefix('cp')
async def entranceFunction(bot, ev):
    s = ev.message.extract_plain_text().split(' ')
    try:
        name = s[0]
        name = s[1]
    except:
        return
    await bot.send(ev, '\n' + getMessage(bot, s), at_sender=True)
