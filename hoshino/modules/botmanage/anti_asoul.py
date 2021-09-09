import re
import asyncio
from PicImageSearch import AsyncGoogle, NetWork
import hoshino
from hoshino import Service, priv, util, R, HoshinoBot
from hoshino.typing import CQEvent, CQHttpError, MessageSegment as ms
from datetime import timedelta

sv = Service('anti-asoul-pic', enable_on_default=True)
anti_asoul = ['嘉然', '嘉人', '夹心糖', '嘉心糖', '乃琳', '贝拉', '珈乐', '向晚', '乃淇淋', '一个魂']

def find_asoul(msg):
    for item in anti_asoul:
        flag = True
        for i in item:
            if not i in msg:
                flag = False
                break
        if flag:
            return True
    return False

@sv.on_message()
async def anti_asoul_pic_f(bot, ev: CQEvent):
    url=''
    for m in ev.message:
        if(m.type == 'image'):
            msg = str(ev.message)
            url = re.findall(r'http.*?term=\d', msg)[0]
            break
    if url and await asoul_pic_search(url):
        priv.set_block_user(ev.user_id, timedelta(minutes=1))
        await util.silence(ev, 60, skip_su=False)
        await bot.send(ev, f'{ms.at(ev.user_id)} 你可少看点虚拟管人吧😅')
        try:
            await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
        except CQHttpError:
            pass
        return
            
    msg = ev.message.extract_plain_text()
    if find_asoul(msg):
        priv.set_block_user(ev.user_id, timedelta(minutes=1))
        await util.silence(ev, 60, skip_su=False)
        await bot.send(ev, f'{ms.at(ev.user_id)} 你可少看点虚拟管人吧😅')
        try:
            await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
        except CQHttpError:
            pass
        return
    return
    
async def asoul_pic_search(url:str)->bool:
    async with NetWork() as client:
        google = AsyncGoogle(client=client)
        res = await google.search(url)

        result=str(res.origin)
        for item in anti_asoul:
            if item in res:
                return True
        return False
