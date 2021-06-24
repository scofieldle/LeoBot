import hoshino
import asyncio
from .base import get_setu
from .config import get_config, get_group_config, set_group_config
from .pixiv import *

HELP_MSG = '''插画搜索 xxx，该搜索功能较弱
插画画师 uid
插画相关 uid
插画日榜 (r18)
插画周榜 (r18)
插画月榜'''
sv = hoshino.Service('pixiv_new', help_=HELP_MSG)

#设置limiter
tlmt = hoshino.util.DailyNumberLimiter(get_config('base', 'daily_max'))
flmt = hoshino.util.FreqLimiter(get_config('base', 'freq_limit'))

def check_lmt(uid):
    if uid in hoshino.config.SUPERUSERS:
        return 0, ''
    if not tlmt.check(uid):
        return 1, f"您今天已经冲过{get_config('base', 'daily_max')}次了,请明天再来!"
    if not flmt.check(uid):
        return 1, f'您冲的太快了,请等待{round(flmt.left_time(uid))}秒!'
    #tlmt.increase(uid,num)
    flmt.start_cd(uid)
    return 0, ''

@sv.on_fullmatch('插画帮助')
async def pixiv_help(bot,ev):
    await bot.send(ev, HELP_MSG)
    
@sv.on_prefix('chahua')
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
        if args[1] == 'pixiv':
            key = 'pixiv'
        elif args[1] == 'pixiv_r18':
            key = 'pixiv_r18'
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
        msg += f'\npixiv : {get_group_config(gid, "pixiv")}'
        msg += f'\npixiv_r18 : {get_group_config(gid, "pixiv_r18")}'
    else:
        msg = 'invalid parameter'
        
    await bot.send(ev,msg)

@sv.on_prefix(('插画画师','插画相关','插画日榜','插画周榜','插画月榜'))
async def send_setu(bot, ev):
    match = str(ev['message'])
    uid = ev['user_id']
    gid = ev['group_id']
    result, msg = check_lmt(uid)
    if result != 0:
        await bot.send(ev, msg)
        return
    
    keyword = ev['prefix']
    r18 = 0
    id = 0
    if ('r18' in match) and get_group_config(gid, 'pixiv_r18'):
            r18 = 1
    if match.isdigit():
        id = int(match)
    await bot.send(ev, '正在搜索...')
    
    try:
        image_list = await query_(keyword, id, r18)
    except:
        await bot.send(ev, '获取图片失败，请检查命令！', at_sender=True)
        return
    
    print(len(image_list))
    if image_list == []:
        await bot.send(ev, '时候未到，不是不报', at_sender=True)
    result_list = []
    msg_ = []
    temp = ''
    for item in image_list:
        temp += str(item['id']) + ' :' + item['title'] + '\n'
        msg = await get_setu(item)
        if msg == None:
            await bot.send(ev, '无可用模块')
            return
        data = {
            "type": "node",
            "data": {
                "name": "小冰",
                "uin": "2854196306",
                "content":msg
                    }
                }
        msg_.append(data)
    msg = {
        "type": "node",
        "data": {
            "name": "小冰",
            "uin": "2854196306",
            "content":temp
                }
            }
    await bot.send_group_forward_msg(group_id=gid, messages=[msg])
        
    try:
        result_list.append(await bot.send_group_forward_msg(group_id=gid, messages=msg_))
    except Exception as e:
        print(e)
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

@sv.on_prefix('插画搜索')
async def send_search_setu(bot, ev):
    keyword = str(ev['message'])
    uid = ev['user_id']
    gid = ev['group_id']
    if not keyword:
        await bot.send(ev, '需要提供关键字')
        return
    result, msg = check_lmt(uid)
    if result != 0:
        await bot.send(ev, msg)
        return

    await bot.send(ev, '正在搜索...')
    msg_list = await query_keyword(keyword)
    if len(msg_list) == 0:
        await bot.send(ev, '无结果')
    msg = await get_setu(msg_list[0])
    data = {
        "type": "node",
        "data": {
            "name": "小冰",
            "uin": "2854196306",
            "content":msg
                }
            }
    
    result_list = []
    try:
        result_list.append(await bot.send_group_forward_msg(group_id=gid, messages=[data]))
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
