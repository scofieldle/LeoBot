# -*- coding: utf-8 -*-
import requests, json, random
from hoshino import Service

sv = Service('jinju', bundle='名言警句', help_='''
金句
'''.strip())

@sv.on_message()
async def jinju(bot, ev):
    num = random.random()
    if num > 0.98:
        url = 'https://v1.hitokoto.cn/' 
        html = requests.get(url, timeout = 3).content
        html = json.loads(str(html, encoding = "utf-8"))
        msg = html['hitokoto'] + '\n' + '----' + html['from']
        await bot.send(ev, msg)
