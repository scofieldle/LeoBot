import hoshino
import asyncio
from .base import *
from .config import get_config, get_group_config, set_group_config

HELP_MSG = '''色图/来n张色图 : 随机获取1张/n张色图
搜[n张]色图 keyword : 搜索指定关键字的色图,附带数量可以获取多张'''
sv = hoshino.Service('setu_mix', bundle='pcr娱乐', help_=HELP_MSG)

#设置limiter
tlmt = hoshino.util.DailyNumberLimiter(get_config('base', 'daily_max'))
flmt = hoshino.util.FreqLimiter(get_config('base', 'freq_limit'))

def China_num(china):
    try:
        temp = int(china)
        return temp
    except:
        pass

    if china == '一':
        return 1
    if china == '二':
        return 2
    if china == '三':
        return 3
    if china == '四':
        return 4
    if china == '五':
        return 5
    if china == '六':
        return 6
    if china == '七':
        return 7
    if china == '八':
        return 8
    if china == '九':
        return 9
    if china == '十':
        return 10

    return 1

def check_lmt(uid, num):
    if uid in hoshino.config.SUPERUSERS:
        return 0, ''
    if not tlmt.check(uid):
        return 1, f"您今天已经冲过{get_config('base', 'daily_max')}次了,请明天再来!"
    if num > 1 and (get_config('base', 'daily_max') - tlmt.get_num(uid)) < num:
            return 1, f"您今天的剩余次数为{get_config('base', 'daily_max') - tlmt.get_num(uid)}次,已不足{num}次,请节制!"
    if not flmt.check(uid):
        return 1, f'您冲的太快了,请等待{round(flmt.left_time(uid))}秒!'
    #tlmt.increase(uid,num)
    flmt.start_cd(uid)
    return 0, ''

@sv.on_prefix('setu')
async def send_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    is_su = hoshino.priv.check_priv(ev, hoshino.priv.SUPERUSER)
    args = ev.message.extract_plain_text().split()

    msg = ''
    if not is_su:
        msg = '需要超级用户权限'
    elif len(args) == 0:
        msg = 'invalid parameter'
    elif args[0] == 'set' and len(args) >= 3: #setu set module on [group]
        if len(args) >= 4 and args[3].isdigit():
            gid = int(args[3])
        key = None
        value = False
        if args[1] == 'lolicon':
            key = 'lolicon'
        elif args[1] == 'lolicon_r18':
            key = 'lolicon_r18'
        elif args[1] == 'withdraw':
            key = 'withdraw'
        if args[2] == 'on' or args[2] == 'true':
            value = True
        elif args[2] == 'off' or args[2] == 'false':
            value = False
        elif args[2].isdigit():
            value = int(args[2])
        if key:
            set_group_config(gid, key, value)
            msg = f'{gid} : {key} = {value}'
        else:
            msg = 'invalid parameter'
    elif args[0] == 'get':
        if len(args) >= 2 and args[1].isdigit():
            gid = int(args[1])
        msg = f'group {gid} :'
        msg += f'\nwithdraw : {get_group_config(gid, "withdraw")}'
        msg += f'\nlolicon : {get_group_config(gid, "lolicon")}'
        msg += f'\nlolicon_r18 : {get_group_config(gid, "lolicon_r18")}'
    elif args[0] == 'fetch':
        await bot.send(ev, 'start fetch mission')
        await fetch_process()
        msg = 'fetch mission complete'
    elif args[0] == 'warehouse':
        msg = 'warehouse:'
        state = check_path()
        for k, v in state.items():
            msg += f'\n{k} : {v}'
    else:
        msg = 'invalid parameter'
        
    await bot.send(ev,msg)

@sv.on_rex(r'^不够[涩瑟色]|^再来[点张份]|^[涩瑟色]图$|^[再]?来?[0-9一二三四五六七八九十][份点张]([涩色瑟]图)')
async def send_random_setu(bot, ev):
    num = 1
    match = str(ev['message'])
    num = China_num(match[1:2])

    uid = ev['user_id']
    gid = ev['group_id']
    result, msg = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msg)
        return

    result_list = []
    msg_ = []
    for _ in range(num):
        msg = await get_setu(gid)
        if msg == None:
            await bot.send(ev, '无可用模块')
            return
        data = {
            "type": "node",
            "data": {
                "name": "妈",
                "uin": "197812783",
                "content":msg
                    }
                }
        msg_.append(data)
        
    try:
        result_list.append(await bot.send_group_forward_msg(group_id=gid, messages=msg_))
    except Exception as e:
        print(e)
        print('图片发送失败')
    await asyncio.sleep(1)

    tlmt.increase(uid, len(result_list))

    second = get_group_config(gid, "withdraw")
    if second and second > 0:
        await asyncio.sleep(second)
        for result in result_list:
            try:
                await bot.delete_msg(self_id=ev['self_id'], message_id=result['message_id'])
            except:
                print('撤回失败')
            await asyncio.sleep(1)

@sv.on_rex(r'^搜[索]?(\d*)[份张]*(.*?)[涩瑟色]图(.*)')
async def send_search_setu(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']

    keyword = ev['match'].group(2) or ev['match'].group(3)
    if not keyword:
        await bot.send(ev, '需要提供关键字')
        return
    keyword = keyword.strip()
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
    msg_list = await search_setu(gid, keyword, num)
    if len(msg_list) == 0:
        await bot.send(ev, '无结果')
    result_list = []
    msg_ = []
    for msg in msg_list:
        data = {
            "type": "node",
            "data": {
                "name": "妈",
                "uin": "197812783",
                "content":msg
                    }
                }
        msg_.append(data)
    try:
        result_list.append(await bot.send_group_forward_msg(group_id=gid, messages=msg_))
    except:
        print('图片发送失败')
    await asyncio.sleep(1)
    tlmt.increase(uid, len(result_list))
    second = get_group_config(gid, "withdraw")
    if second and second > 0:
        await asyncio.sleep(second)
        for result in result_list:
            try:
                await bot.delete_msg(self_id=ev['self_id'], message_id=result['message_id'])
            except:
                print('撤回失败')
            await asyncio.sleep(1)
            
@sv.scheduled_job('interval', minutes=30)
async def job():
    await fetch_process()
