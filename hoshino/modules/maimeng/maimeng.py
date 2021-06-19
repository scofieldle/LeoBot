import os
import random
import re
import aiohttp
import filetype
import nonebot
from nonebot.exceptions import CQHttpError
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from os import path
from typing import List, Union
from hoshino import R, Service, priv
from hoshino.util import FreqLimiter, DailyNumberLimiter
from aiocqhttp.event import Event
from aiocqhttp.exceptions import ActionFailed
import time
import hashlib
import asyncio
import filetype

_max = 5
EXCEED_NOTICE = f'一天戳{_max}次还不够吗？！'
_nlmt = DailyNumberLimiter(_max)
_flmt = FreqLimiter(3)

sv = Service('maimeng')
maimeng_folder = R.img('maimeng/').path

def maimeng_gener():
    while True:
        filelist = os.listdir(maimeng_folder)
        random.shuffle(filelist)
        for filename in filelist:
            if os.path.isfile(os.path.join(maimeng_folder, filename)):
                if 'jpg' in filename or 'png' in filename:
                    yield R.img('maimeng/', filename)

maimeng_gener = maimeng_gener()

def get_maimeng():
    return maimeng_gener.__next__()


@sv.on_notice('notify.poke')
async def maimeng(session: NoticeSession):
    uid = session.ctx['user_id']
    at_user = MessageSegment.at(session.ctx['user_id'])
    guid = session.ctx['group_id'], session.ctx['user_id']
    if not _nlmt.check(uid):
        await session.send(EXCEED_NOTICE)
        return
    if not _flmt.check(uid):
        await session.send(f'太快了啦，人家也要时间准备的{at_user}')
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)

    # conditions all ok, send a maimeng.
    pic = get_maimeng()
    try:
        await session.send(pic.cqcode)
    except CQHttpError:
        sv.logger.error(f"发送图片{pic.path}失败")
        try:
            await session.send(f'啊嘞，好像发送失败了')
        except:
            pass