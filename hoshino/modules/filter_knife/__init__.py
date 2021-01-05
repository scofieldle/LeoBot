from hoshino import Service
import copy
import sqlite3
import aiohttp
import json
import os
import hoshino

yobot_url = 'http://127.0.0.1:22/yobot/' 
    # 获取主页地址：在群内向bot发送指令“手册”，复制bot发送的链接地址，删除末尾的manual/后即为主页地址
    # 例:https://域名/目录/或http://IP地址:端口号/目录/,注意不要漏掉最后的斜杠！

DB_PATH = '/home/ubuntu/HoshinoBot/hoshino/modules/yobot/yobot/src/client/yobot_data/yobotdata.db'
    # 例：C:/Hoshino/hoshino/modules/yobot/yobot/src/client/yobot_data/yobotdata.db
    # 注意斜杠方向！！！

#==============================================




filter_knife_data = {
    # "QQ群号":{
    #     "QQ号":{
    #         "damage":12345,
    #         "name":"QQ名"
    #     }
    #     }
}

boss_HP = {
    # "QQ群号":boss生命值
}

damage_ranking = {}

TXT_LEN = 12


sv = Service("filter_knife")

help_txt = '''
公会战筛刀插件
[开始筛刀]           清空以前的筛刀数据
[筛刀 伤害值 @群友]  把筛刀数据报给机器人，如果手里有多个账号可以用@代报，自己的筛刀不需要@
[筛刀信息]           显示现在的筛刀信息
[结算 编号]          提醒筛刀信息里某人结算出刀，编号是筛刀信息里的编号
[结束筛刀]           清空当前筛刀数据

注意筛刀信息没有做持久化，如果筛刀过程中机器人重启会丢失当前筛刀数据
筛刀时会读取出刀数据获取boss当前生命值，所以当前公会战至少要报过一刀有出刀数据才行
注意新创建的公会有时候会获取不到apikey
'''




def get_apikey(gid:str) -> str:
    # 获取apikey
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f'select apikey from clan_group where group_id={gid}')
    apikey = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return apikey


async def get_boss_hp(gid:str) -> str:

    apikey = get_apikey(gid)
    url = f'{yobot_url}clan/{gid}/statistics/api/?apikey={apikey}'

    session = aiohttp.ClientSession()
    async with session.get(url) as resp:
        data = await resp.json()
        boss_hp = data["challenges"][-1]["health_ramain"]  # 获取最后一刀的boss血量

        return boss_hp

def get_compensate_time(_damage,gid):
    damage = int(_damage)
    if boss_HP[gid] > damage:
        return "无法击杀BOSS"

    compensate_time = (1 - boss_HP[gid] / damage)*90+10
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

    mes = "当前筛刀信息如下：\n"
    mes += f"BOSS生命值：{boss_HP[gid]}   当前筛刀人数 {len(filter_knife_data[gid])}   当前筛刀总伤害 {all_damage}\n"
    mes += f"编号 {center('用户名')}{center('伤害')}{center('击杀补偿时间')}\n"
    for i in range(len(test_uid_list)):
        mes += f"{i+1}.   {center(filter_knife_data[gid][test_uid_list[i]]['name'])}{center(filter_knife_data[gid][test_uid_list[i]]['damage'])}{center(get_compensate_time(filter_knife_data[gid][test_uid_list[i]]['damage'],gid))}\n"

    return mes



@sv.on_prefix(["开始筛刀","结束筛刀","筛刀开始","筛刀结束"])
async def _ (bot, ev):
    gid = str(ev['group_id'])
    if len(yobot_url) == 0:
        await bot.send(ev, f'获取api地址失败，请检查配置')
        return
    if not get_db_path():
        await bot.send(ev, f'获取数据库路径失败，请检查配置')
        return
    if gid in boss_HP:
        boss_HP.pop(gid)
    filter_knife_data[gid] = {}
    await bot.send(ev, "已清空以前的筛刀数据")




@sv.on_prefix("筛刀")
async def _ (bot, ev):
    damage = ev.message.extract_plain_text().strip()
    if not damage.isdigit() :
        await bot.send(ev, "伤害值不能转换为数字",at_sender=True)
        return

    damage = int(damage)
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

    await bot.send(ev, "已记录筛刀信息", at_sender=True)




@sv.on_prefix("更新筛刀")
async def _ (bot, ev):
    damage = ev.message.extract_plain_text().strip()
    if not damage.isdigit() :
        await bot.send(ev, "伤害值不能转换为数字",at_sender=True)
        return

    damage = int(damage)
    gid = str(ev['group_id'])
    uid = str(ev['user_id'])

    for m in ev['message']:
        if m['type'] == 'at' and m['data']['qq'] != 'all':
        # 检查消息有没有带@信息，有的话uid改为@的QQ号
            uid = str(m['data']['qq'])

    filter_knife_data[gid][uid]["damage"] = damage
    await bot.send(ev, "已更新筛刀伤害", at_sender=True)


@sv.on_prefix(["筛刀结算","结算筛刀","出来","结算"])
async def _ (bot, ev):

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
    mes = f"[CQ:at,qq={uid}] 请结算伤害为 {pop['damage']} 的出刀，游戏结算后尽快报刀"
    await bot.send(ev, mes)
    await bot.send(ev, get_filter_knife_info(gid))


@sv.on_prefix(["筛刀信息"])
async def _ (bot, ev):
    gid = str(ev['group_id'])

    boss_HP[gid] = int(await get_boss_hp(gid))
    gid = str(ev['group_id'])
    await bot.send(ev, get_filter_knife_info(gid))


@sv.on_prefix(["筛刀帮助"])
async def _ (bot, ev):
    await bot.send(ev, help_txt)
