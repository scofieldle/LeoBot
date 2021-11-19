#encoding:utf-8
import os, random, re, pprint, json, math, asyncio, threading
import traceback
from io import BytesIO
from PIL import Image
from collections import defaultdict
from datetime import datetime
import nonebot
from hoshino import R, Service, priv, util
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter
from .akgacha import *
from .prtsres import *
from urllib import request

working_path = "hoshino/modules/akgacha/"
img_path = "./images"
char_data = json.load(open(working_path + "character_table.json", encoding="utf-8"))
gacha_data = json.load(open(working_path + "config.json", encoding="utf-8"))

sv_help = '''
[@Bot方舟十连] 明日方舟抽卡
[@Bot方舟来一井] 龙门币算什么，看我18w合成玉
[查看方舟卡池] 当前卡池信息
[切换方舟卡池] 更改卡池
[查看方舟历史卡池] 查看可抽的所有卡池
------
管理命令:
[更新方舟基础数据] 更新角色数据库
[更新方舟卡池] 更新卡池信息
[更新方舟资源] 下载头像包到/res/img/akgacha/
'''.strip()
sv = Service('akgacha', help_=sv_help, bundle="akgacha", enable_on_default=True)

jewel_limit = DailyNumberLimiter(18000)
tenjo_limit = DailyNumberLimiter(3)

JEWEL_EXCEED_NOTICE = f"您今天已经抽过{jewel_limit.max}钻了，欢迎明早5点后再来！"

TENJO_EXCEED_NOTICE = f"您今天已经抽过{tenjo_limit.max}张天井券了，欢迎明早5点后再来！"

group_banner = {}
try:
    group_banner = json.load(open(working_path + "group_banner.json", encoding="utf-8"))
except FileNotFoundError: pass
    
def save_group_banner():
    with open(working_path + "group_banner.json", "w", encoding="utf-8") as f:
        json.dump(group_banner, f, ensure_ascii=False)
        
def ak_group_init(gid):
    group_banner[gid] = { "banner": "普池#52", "weibo_check": datetime.now().timestamp(), "weibo_push": False }
        
@sv.on_fullmatch(("查看方舟卡池"))
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if not gid in group_banner:
        ak_group_init(gid)
    banner = group_banner[gid]["banner"]
    gacha = Gacha()
    gacha.set_banner(banner)
    line = gacha.explain_banner()
    await bot.send(ev, line)

@sv.on_prefix(("切换方舟卡池"))
async def set_pool(bot, ev: CQEvent):
    name = util.normalize_str(ev.message.extract_plain_text())
    if not name:
        # 列出当前卡池
        current_time=datetime.now().timestamp()
        list_cur=[]
        for gacha in gacha_data["banners"]:
            if int(gacha_data["banners"][gacha]["end"])>int(current_time):
                list_cur.append(gacha)
        if list_cur:
            lines = ["当期卡池:"] + list_cur + ["", "使用命令[切换方舟卡池 （卡池名）]进行设置","使用命令[查看方舟历史卡池]查看全部往期卡池"]
            await bot.finish(ev, "\n".join(lines))
        else:
            await bot.finish(ev, "未找到正在进行中的卡池……请联系维护组更新卡池信息或使用命令[查看方舟历史卡池]查看全部往期卡池")
    else:
        if name in gacha_data["banners"].keys():
            gid = str(ev.group_id)
            group_banner[gid]["banner"] = name
            save_group_banner()
            await bot.send(ev, f"卡池已经切换为 {name}", at_sender=True)
            await gacha_info(bot, ev)
        else:
            await bot.finish(ev, f"没找到卡池: {name}")
            
@sv.on_fullmatch(("查看方舟历史卡池","查看舟游历史卡池"))
async def history_pool(bot, ev: CQEvent):
    lines = ["全部卡池:"] + list(gacha_data["banners"].keys()) + ["", "使用命令 切换方舟卡池 x（x为卡池名）进行设置"]
    msg = [{"type": "node","data": {"name": "小冰","uin": "2854196306","content":"\n".join(lines)}}]
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)

async def check_jewel(bot, ev):
    if not jewel_limit.check(ev.user_id):
        await bot.finish(ev, JEWEL_EXCEED_NOTICE, at_sender=True)
    elif not tenjo_limit.check(ev.user_id):
        await bot.finish(ev, TENJO_EXCEED_NOTICE, at_sender=True)

@sv.on_prefix(("方舟十连"))
async def gacha_10(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if not gid in group_banner:
        ak_group_init(gid)
    b = group_banner[gid]["banner"]
    
    # barrier
    await check_jewel(bot, ev)
    jewel_limit.increase(ev.user_id, 6000)
    
    g = Gacha()
    g.set_banner(b)
    g.rare_chance = False
    result = g.ten_pull()
    await bot.send(ev, g.summarize_tenpull(result), at_sender=True)

@sv.on_prefix(("方舟来一井"))
async def gacha_300(bot, ev: CQEvent):
    gid = str(ev.group_id)
    if not gid in group_banner:
        ak_group_init(gid)
    b = group_banner[gid]["banner"]
    
    # barrier
    await check_jewel(bot, ev)
    tenjo_limit.increase(ev.user_id)
    
    g = Gacha()
    g.set_banner(b)
    if b == "r6":
        for i in range(0, 12):
            g.ten_pull()
        await bot.send(ev, g.summarize(True), at_sender=True)
    else:
        for i in range(0, 30):
            g.ten_pull()
        await bot.send(ev, g.summarize(), at_sender=True)
    
@sv.on_fullmatch(("方舟刷本效率"))
async def show_mats(bot, ev: CQEvent):
    img = MessageSegment.image(f'file:///{os.path.abspath(working_path + "ak-mats.jpg")}')
    line = f'{img}\n明日方舟素材刷取一图流-等效绿票算法版\nhttps://hguandl.com/yituliu/yituliu.jsp'
    await bot.send(ev, line)

def save_pic(url):
    filename = working_path + "cache/" + os.path.basename(url)
    if os.path.exists(filename):
        print("save_pic: file exists - %s" % filename)
    else:
        resp = request.urlopen(url)
        img = resp.read()
        filename = working_path + "cache/" + os.path.basename(url)
        print("save_pic %s" % filename)
        with open(filename, "wb+") as f:
            f.write(img)
    return filename

@sv.on_fullmatch(("更新方舟数据","更新舟游数据"))
async def update(bot, ev: CQEvent):
    global char_data
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev,'此命令仅维护组可用，请联系维护组~')
        return
    await bot.send(ev, '正在更新请稍候……')
    try:
        await update_table()
        await bot.send(ev, '更新基础数据成功！')
        await update_pool()
        await bot.send(ev, '更新卡池成功！')
        result = await update_res()
        await bot.send(ev, '更新资源成功！')
    except Exception as e:
        print(format_exc())
        await bot.send(ev, f'更新失败……{e}')
    
async def update_table():
    global char_data
    result = await update_chara_db()
    if result:
        data_init()
        char_data = json.load(open(os.path.join(working_path, "character_table.json"), encoding="utf-8"))

async def update_pool():
    global gacha_data
    result = await update_config()
    if result:
        data_init()
        gacha_data = json.load(open(os.path.join(working_path, "config.json"), encoding="utf-8"))

