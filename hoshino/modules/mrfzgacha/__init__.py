import os
import random
from collections import defaultdict

from hoshino import Service, priv, util
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter, concat_pic, pic2b64, silence

from .config import *
from .chara import *
from nonebot import MessageSegment
from .gacha import Gacha

try:
    import ujson as json
except:
    import json


sv_help = '''
[抽干员] 300抽！
[查看卡池] 模拟卡池&出率
'''.strip()
sv = Service('mrfzgacha', help_=sv_help, bundle='mrfz娱乐')
jewel_limit = DailyNumberLimiter(6000)
tenjo_limit = DailyNumberLimiter(1)

TENJO_EXCEED_NOTICE = f'您今天已经抽过{tenjo_limit.max}张天井券了，欢迎明早5点后再来！'

gacha_300_aliases = ('抽干员')


@sv.on_fullmatch(('卡池资讯', '查看卡池', '看看卡池', '康康卡池', '卡池資訊', '看看up', '看看UP'))
async def gacha_info(bot, ev: CQEvent):
    gacha = Gacha()
    up_chara = gacha.up
    up_chara = map(lambda x: str(fromname(x, star=3).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await bot.send(ev, f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%")

async def check_tenjo_num(bot, ev: CQEvent):
    if not tenjo_limit.check(ev.user_id):
        await bot.finish(ev, TENJO_EXCEED_NOTICE, at_sender=True)


@sv.on_prefix(gacha_300_aliases, only_to_me=True)
async def gacha_300(bot, ev: CQEvent):

    await check_tenjo_num(bot, ev)
    tenjo_limit.increase(ev.user_id)

    gacha = Gacha()
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg = [
        f"\n素敵な仲間が増えますよ！ {res}",
        f"★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"获得记忆碎片×{100*up}与女神秘石×{50*(up+s3) + 10*s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得女神秘石{50*(up+s3) + 10*s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有12.16%")
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > 290:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 250:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")

    await bot.send(ev, '\n'.join(msg), at_sender=True)
    silence_time = (100*up + 50*(up+s3) + 10*s2 + s1) * 1
    await silence(ev, silence_time)


@sv.on_prefix('氪金')
async def kakin(bot, ev: CQEvent):
    if ev.user_id not in bot.config.SUPERUSERS:
        return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            jewel_limit.reset(uid)
            tenjo_limit.reset(uid)
            count += 1
    if count:
        await bot.send(ev, f"已为{count}位用户充值完毕！谢谢惠顾～")
