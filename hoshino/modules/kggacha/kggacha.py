import os
import random
import os
from hoshino import Service
from hoshino.typing import *
from hoshino.util import concat_pic, pic2b64, silence
from . import chara
from .chara import *
from .gacha import Gacha

try:
    import ujson as json
except:
    import json


sv_help = '''
[坎十连] 转蛋模拟
[坎单抽] 转蛋模拟
[坎来一井] 300连！
[查看卡池坎] 模拟卡池&出率
'''.strip()
sv = Service('kggacha', help_=sv_help, bundle='通用')

gacha_10_aliases = ('k10')
gacha_1_aliases = ('k一发')
gacha_300_aliases = ('坎公启动','坎公一井', 'k一井','k300','k#')


file_path = os.path.split(os.path.realpath(__file__))[0]
_pool_config_file = os.path.expanduser(f'{file_path}/yuanshen_config.json')
_group_pool = {}
try:
    with open(_pool_config_file, encoding='utf8') as f:
        _group_pool = json.load(f)
except FileNotFoundError as e:
    sv.logger.warning('yuanshen_config.json not found, will create when needed.')

def dump_pool_config():
    with open(_pool_config_file, 'w', encoding='utf8') as f:
        json.dump(_group_pool, f, ensure_ascii=False)

@sv.on_fullmatch(('查看坎公骑角色卡池', '看看坎公骑角色up'))
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    print(gid)
    gacha = Gacha(_group_pool["1"])
    up_chara = gacha.up
    up_chara = map(lambda x: str(chara.fromname(x, star=3).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await bot.send(ev, f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%")


@sv.on_prefix(gacha_1_aliases, only_to_me=False)
async def gacha_1_k(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    gacha = Gacha(_group_pool["1"])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60
    res = f'{chara.icon.cqcode} {chara.name} {"★"*chara.star}'
    await silence(ev, silence_time)
    await bot.send(ev, f'恭喜骑士出货了！\n{res}', at_sender=True)


@sv.on_prefix(gacha_10_aliases, only_to_me=False)
async def gacha_10_k(bot, ev: CQEvent):
    SUPER_LUCKY_LINE = 170
    gid = ev.group_id
    uid = ev.user_id
    gacha = Gacha(_group_pool["1"])
    result, hiishi = gacha.gacha_ten()
    # silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60
    res1 = chara.gen_team_pic(result[:5], star_slot_verbose=False)
    res2 = chara.gen_team_pic(result[5:], star_slot_verbose=False)
    res = concat_pic([res1, res2])
    res = pic2b64(res)
    res = MessageSegment.image(res)
    result = [f'{c.name}{"★"*c.star}' for c in result]

    if hiishi >= SUPER_LUCKY_LINE:
        await bot.send(ev, '恭喜海豹！你的喜悦我收到了，滚去喂鲨鱼吧！！')
    await bot.send(ev, f'恭喜骑士出货了！\n{res}\n', at_sender=True)


@sv.on_prefix(gacha_300_aliases, only_to_me=False)
async def gacha_300_k(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    gacha = Gacha(_group_pool["1"])
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    step = 4
    pics = []
    for i in range(0, lenth, step):
        j = min(lenth, i + step)
        pics.append(chara.gen_team_pic(res[i:j], star_slot_verbose=False))
    res = concat_pic(pics)
    res = pic2b64(res)
    res = MessageSegment.image(res)

    msg = [
        f"\n恭喜骑士出货了！ {res}",
        f"★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"\n第{result['first_up_pos']}抽首次获得up角色"
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
    elif up >= 4:
        msg.append("您是托吧？")
    await bot.send(ev, '\n'.join(msg), at_sender=True)