from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
import hoshino
from .data import *

sv = Service('doujin')

FREQ_LIMIT = 10
DAILY_MAX = 5

# 设置limiter
tlmt = hoshino.util.DailyNumberLimiter(DAILY_MAX)
flmt = hoshino.util.FreqLimiter(FREQ_LIMIT)
_tlmt = DailyNumberLimiter(5)

def list_to_forward(li, ev):
    temp = []
    for each in li:
        data = {
            "type": "node",
            "data": {
                "name": '妈',
                "uin": '197812783',
                "content": each
            }
        }
        temp.append(data)
    return temp

def check_lmt(uid, num):
    if uid in hoshino.config.SUPERUSERS:
        return 0, ''
    if not tlmt.check(uid):
        return 1, f"你今天已经看过{DAILY_MAX}次本子了,请明天再来!"
    if num > 1 and (DAILY_MAX - tlmt.get_num(uid)) < num:
        return 1, f"你今天的剩余次数为{DAILY_MAX - tlmt.get_num(uid)}次,已不足{num}次,请节制!"
    if not flmt.check(uid):
        return 1, f'您冲的太快了,请等待{round(flmt.left_time(uid))}秒!'
    # tlmt.increase(uid,num)
    flmt.start_cd(uid)
    return 0, ''


@sv.on_rex(r'^再来[点份]|^本子$|^[再]?来?(\d*)?[份](本子)')
async def send_random_doujin(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    num = 1
    match = ev['match']
    try:
        num = int(match.group(1))
    except:
        pass
    result, msg = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msg)
        return
    await bot.send(ev, '开始处理本子')
    doujins = get_random_doujin_list(num)
    for each in doujins:
        msg = get_msg_by_doujin(each)
        data = list_to_forward(msg, ev)
        await bot.send(ev, '本子处理完毕')
        await bot.send_group_forward_msg(group_id = gid, messages=data)

@sv.on_rex(r'^搜[索]?(\d*)[份张]*(.*?)本子(.*)')
async def send_search_doujin(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    keyword = ev['match'].group(2) or ev['match'].group(3)
    if not keyword:
        await bot.send(ev, '需要提供关键字')
        return
    keyword = keyword.strip()
    print(keyword)
    num = ev['match'].group(1)
    if num:
        num = int(num.strip())
    else:
        num = 1
    result, msg = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msg)
        return
    await bot.send(ev, '正在搜索...')
    doujins = get_search_doujin_list(keyword, num)
    for each in doujins:
        msg = get_msg_by_doujin(each)
        data = list_to_forward(msg, ev)
        await bot.send_group_forward_msg(group_id = gid, message=data)
