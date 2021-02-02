import copy
import sqlite3
import aiohttp
import json
import os
import hoshino

help_txt = '''
公会战筛刀插件
[开始筛刀]           清空以前的筛刀数据
[筛刀 伤害值 @群友]  把筛刀数据报给机器人，如果手里有多个账号可以用@代报，自己的筛刀不需要@
[筛刀信息]           显示现在的筛刀信息
[结算 编号]          提醒筛刀信息里某人结算出刀，编号是筛刀信息里的编号
[结束筛刀]           清空当前筛刀数据
[合刀 伤害1 伤害2]   计算指定两刀补偿时间 
[筛刀帮助]           查看帮助 

注意筛刀信息没有做持久化，如果筛刀过程中机器人重启会丢失当前筛刀数据
筛刀时会读取出刀数据获取boss当前生命值，所以当前公会战至少要报过一刀有出刀数据才行
注意新创建的公会有时候会获取不到apikey'''

sv = hoshino.Service('knife_filter', bundle='pcr筛刀插件', help_=help_txt)

db_path = "./hoshino/modules/yobot/yobot/src/client/yobot_data/yobotdata.db"

yobot_url = "http://127.0.0.1:9222/yobot/"

filter_knife_data = {}

boss_HP = {}

damage_ranking = {}

TXT_LEN = 12

def get_apikey(gid):
    # 获取apikey
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f'select apikey from clan_group where group_id={gid}')
    apikey = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return apikey

async def get_boss_hp(gid):
    apikey = get_apikey(gid)
    url = f'{yobot_url}clan/{gid}/statistics/api/?apikey={apikey}'

    session = aiohttp.ClientSession()
    async with session.get(url) as resp:
        data = await resp.json()
        boss_hp = data["challenges"][-1]["health_ramain"]  # 获取最后一刀的boss血量
        return boss_hp

def get_compensate_time(boss_hp, _damage):
    damage = int(_damage)
    if boss_hp > damage:
        return "无法击杀BOSS"

    compensate_time = (1 - boss_hp / damage)*90+10
    return f"返还 {int(compensate_time)} 秒"

def center(_txt):
    # 在字符串前后加空格格式化输出
    txt = str(_txt)
    return txt.center(TXT_LEN," ")

def get_filter_knife_info(gid):
    if not gid in filter_knife_data:
        return "当前没有筛刀信息"
    if not filter_knife_data[gid]:
        return "当前没有筛刀信息"

    all_damage = 0
    all_damage_list = []
    print(filter_knife_data)
    for uid in filter_knife_data[gid]:
        print(uid)
        all_damage_list.append(filter_knife_data[gid][uid]["damage"])

    for damage in all_damage_list:
        all_damage += damage

    # 排序把列表反向
    all_damage_list.sort()
    all_damage_list.reverse()

    # 拷贝出一份数据来把uid按伤害值从大到小放到test_uid_list
    test_dict = copy.deepcopy(filter_knife_data[gid])
    test_uid_list = []

    for damage in all_damage_list:
        for uid in test_dict.keys():
            if test_dict[uid]["damage"] == damage:
                test_uid_list.append(uid)
                test_dict.pop(uid)
                break

    damage_ranking[gid] = copy.deepcopy(test_uid_list)
    boss_hp = boss_HP[gid] - filter_knife_data[gid][test_uid_list[0]]['damage']

    mes = "当前筛刀信息如下：\n"
    mes += f"BOSS生命值：{boss_HP[gid]}\n当前筛刀人数:{len(filter_knife_data[gid])}\n当前筛刀总伤害:{all_damage}\n"
    mes += f"编号 {center('用户名')}{center('伤害')}{center('备注')}{center('与1号合刀补偿时间')}\n"
    for i in range(len(test_uid_list)):
        rest_time = get_compensate_time(boss_hp,filter_knife_data[gid][test_uid_list[i]]['damage'])
        mes += f"{i+1}.{center(filter_knife_data[gid][test_uid_list[i]]['name'])}{center(filter_knife_data[gid][test_uid_list[i]]['damage'])}{center(filter_knife_data[gid][test_uid_list[i]]['margin'])}{center(rest_time)}\n"

    return mes

@sv.on_prefix(('开始筛刀','结束筛刀','筛刀开始','筛刀结束'))
async def start(bot, ev):
    gid = str(ev['group_id'])
    if len(yobot_url) == 0:
        await bot.send(ev, f'获取api地址失败，请检查配置')
        return
    if gid in boss_HP:
        boss_HP.pop(gid)
    filter_knife_data[gid] = {}
    await bot.send(ev, "已清空以前的筛刀数据")


@sv.on_prefix('筛刀')
async def shai (bot, ev):
    content = ev.message.extract_plain_text().split(' ')

    damage = content[0]
    if 'w' in damage or 'W' in damage:
        damage = int(float(damage[:-1]) * 10000)
    else:
        damage = int(damage)

    try:
        margin = content[1]
    except:
        margin = '无备注'
    gid = str(ev['group_id'])
    uid = str(ev['user_id'])
    name = str(ev['sender']['card'])

    for m in ev['message']:
        if m['type'] == 'at' and m['data']['qq'] != 'all':
        # 检查消息有没有带@信息，有的话uid改为@的QQ号
            uid = str(m['data']['qq'])

    if name == "":
        name = str(ev['sender']['nickname'])
    if not (gid in filter_knife_data):
        filter_knife_data[gid] = {}
    if uid in filter_knife_data[gid]:
        await bot.send(ev, "你已经参加过本次筛刀了\n如果伤害填写错误请使用 [更新筛刀 伤害]", at_sender=True)
        return

    if not (gid in boss_HP):
        boss_HP[gid] = int(await get_boss_hp(gid))

    filter_knife_data[gid][uid] = {}
    filter_knife_data[gid][uid]["name"] = name
    filter_knife_data[gid][uid]["damage"]  = damage
    filter_knife_data[gid][uid]["margin"]  = margin

    await bot.send(ev, "已记录筛刀信息", at_sender=True)


@sv.on_prefix('更新筛刀')
async def update (bot, ev):
    content = ev.message.extract_plain_text().split(' ')

    damage = content[0]
    if 'w' in damage or 'W' in damage:
        damage = int(float(damage[:-1]) * 10000)
    else:
        damage = int(damage)

    try:
        margin = content[1]
    except:
        margin = '无'
    
    gid = str(ev['group_id'])
    uid = str(ev['user_id'])

    for m in ev['message']:
        if m['type'] == 'at' and m['data']['qq'] != 'all':
        # 检查消息有没有带@信息，有的话uid改为@的QQ号
            uid = str(m['data']['qq'])

    filter_knife_data[gid][uid]["damage"] = damage
    filter_knife_data[gid][uid]["margin"]  = margin
    await bot.send(ev, "已更新筛刀伤害", at_sender=True)

@sv.on_prefix(('筛刀结算','结算筛刀','出来','结算'))
async def finish (bot, ev):
    gid = str(ev['group_id'])
    number = ev.message.extract_plain_text().strip()
    if not gid in boss_HP :
        # 如果boss_HP没有数据表示没筛刀，这次是误触发
        return
    if not number.isdigit():
        await bot.send(ev, "你需要输入一个正确编号", at_sender=True)

    number = int(number)
    uid = damage_ranking[gid].pop(number-1)
    pop = filter_knife_data[gid].pop(uid)
    mes = f"[CQ:at,qq={uid}] 请结算伤害为 {pop['damage']} 的出刀，结算后尽快报刀"
    await bot.send(ev, mes)
    await bot.send(ev, get_filter_knife_info(gid))

@sv.on_prefix('筛刀信息')
async def info (bot, ev):
    gid = str(ev['group_id'])

    boss_HP[gid] = int(await get_boss_hp(gid))
    gid = str(ev['group_id'])
    await bot.send(ev, get_filter_knife_info(gid))


@sv.on_prefix('筛刀帮助')
async def help (bot, ev):
    await bot.send(ev, help_txt)

@sv.on_prefix('合刀')
async def feedback(bot, ev):
    gid = str(ev['group_id'])
    cmd = ev.raw_message
    content=cmd.split()
    if(len(content)!=3):
        reply="请输入：合刀 刀1伤害 刀2伤害"
        await bot.send(ev, reply)
        return
    d1=float(content[1])
    d2=float(content[2])
    rest=boss_HP[gid]
    if(d1+d2<rest):
        reply="醒醒！这两刀是打不死boss的\n"
        await bot.send(ev, reply)
        return
        
    dd1=d1
    dd2=d2
    if d1>=rest:
        dd1=rest
    if d2>=rest:
        dd2=rest        
    res1=(1-(rest-dd1)/dd2)*90+10; # 1先出，2能得到的时间
    res2=(1-(rest-dd2)/dd1)*90+10; # 2先出，1能得到的时间
    res1=round(res1,2)
    res2=round(res2,2)
    res1=min(res1,90)
    res2=min(res2,90)
    res1=str(res1)
    res2=str(res2)
    reply=""
    if(d1>=rest or d2>=rest):
        reply=reply+"注：\n"
        if(d1>=rest):
            reply=reply+"第一刀可直接秒杀boss，伤害按 "+str(rest)+" 计算\n"
        if(d2>=rest):
            reply=reply+"第二刀可直接秒杀boss，伤害按 "+str(rest)+" 计算\n"
    d1=str(d1)
    d2=str(d2)
    reply=reply+d1+"先出，另一刀可获得 "+res1+" 秒补偿刀\n"
    reply=reply+d2+"先出，另一刀可获得 "+res2+" 秒补偿刀\n"
    await bot.send(ev, reply)