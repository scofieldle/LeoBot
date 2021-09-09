# -*- coding: utf-8 -*-
import os
import random
from hoshino import Service

sv = Service('reply', bundle='随机回复')

path = os.path.dirname(__file__)

def readInfo(file):
    file_path = os.path.join(path,f'{file}.txt')
    print(file_path)
    data = []
    with open(file_path,'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            data.append(line)
            line = f.readline()
    txt = ''
    while not txt:
        txt = random.choice(data)
        if file != 'emoji':
            if len(txt) < 8:
                txt = ''
    return txt
    
@sv.on_message()
async def random_reply(bot, ev):
    num = random.random()
    if num > 0.998:
        file = random.choice(['emoji','jueju','maren','qinghua','zhonger','zhongyi'])
        txt = readInfo(file).replace('\n','')

        await bot.send(ev, txt)
        
@sv.on_fullmatch('对话')
async def reply(bot, ev):
    file = random.choice(['emoji','jueju','maren','qinghua','zhonger','zhongyi'])
    txt = readInfo(file).replace('\n','')

    await bot.send(ev, txt)
