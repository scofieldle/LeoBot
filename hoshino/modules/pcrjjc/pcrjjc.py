from json import load, dump
from nonebot import get_bot
from hoshino import Service, priv
from hoshino.typing import NoticeSession
from .pcrclient import pcrclient, ApiException
from threading import Lock
from os.path import dirname, join, exists
from  datetime import datetime, timezone, timedelta
import signal

sv_help = '''
[竞技场绑定 uid] 绑定竞技场排名变动推送（仅下降），默认双场均启用
[竞技场查询 (uid)] 查询竞技场简要信息
[停止竞技场订阅] 停止战斗竞技场排名变动推送
[停止公主竞技场订阅] 停止公主竞技场排名变动推送
[启用竞技场订阅] 启用战斗竞技场排名变动推送
[启用公主竞技场订阅] 启用公主竞技场排名变动推送
[删除竞技场订阅] 删除竞技场排名变动推送绑定
[竞技场订阅状态] 查看排名变动推送绑定状态
[竞技场私聊] 暂时关闭
'''

sv = Service('竞技场推送',help_=sv_help, bundle='pcr查询')

@sv.on_fullmatch('jjc帮助', only_to_me=False)
async def send_jjchelp(bot, ev):
    await bot.send(ev, sv_help)

curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'arena_bind' : {}
}

cache = {}
client = None
lck = Lock()

if exists(config):
    with open(config) as fp:
        root = load(fp)

binds = root['arena_bind']

with open(join(curpath, 'account.json')) as fp:
    client = pcrclient(load(fp))

# 自定义超时异常
class TimeoutError(Exception):
    def __init__(self, msg):
        super(TimeoutError, self).__init__()
        self.msg = msg

def time_out(interval, callback):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError("run func timeout")

        def wrapper(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(interval)       # interval秒后向进程发送SIGALRM信号
                result = func(*args, **kwargs)
                signal.alarm(0)              # 函数在规定时间执行完后关闭alarm闹钟
                return result
            except:
                callback("run func timeout")
        return wrapper
    return decorator

def timeout_callback(e):
    print(e.msg)
  
@time_out(6, timeout_callback)
async def query(id:str):
    while client.shouldLogin:
        await client.login()
    return (await client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        }))['user_info']

def save_binds():
    with open(config, 'w') as fp:
        dump(root, fp, indent=4)

@sv.on_rex(r'^竞技场绑定 ?(\d{13})$')
async def on_arena_bind(bot, ev):
    global binds, lck

    while not lck.locked():
        with lck:
            uid = str(ev['user_id'])
            last = binds[uid] if uid in binds else None

            binds[uid] = {
                'id': ev['match'].group(1),
                'uid': uid,
                'gid': str(ev['group_id']),
                'arena_on': last is None or last['arena_on'],
                'grand_arena_on': last is None or last['grand_arena_on'],
                'private': True,
            }
            save_binds()
        break

    await bot.finish(ev, '竞技场绑定成功', at_sender=True)

@sv.on_fullmatch(('竞技场查询','查询竞技场'))
async def on_query_arena(bot, ev):
    global binds, lck

    while not lck.locked():
        with lck:
            uid = str(ev['user_id'])
            if not uid in binds:
                await bot.finish(ev, '您还未绑定竞技场', at_sender=True)
                return
            else:
                id = binds[uid]['id']
                #失效ID刷新
                if not binds[uid]['private']:
                    binds[uid]['private'] = True
                    save_binds()
            try:
                res = await query(id)
                msg =f'''竞技场排名：{res["arena_rank"]}\n公主竞技场排名：{res["grand_arena_rank"]}'''
                await bot.finish(ev, msg)
            except ApiException as e:
                await bot.finish(ev, f'查询出错，{e}', at_sender=True)
        break

@sv.on_fullmatch(('删除竞技场订阅','取消竞技场订阅','解除竞技场订阅'))
async def delete_arena_sub(bot,ev):
    global binds, lck

    uid = str(ev['user_id'])

    if ev.message[0].type == 'at':
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '删除他人订阅请联系维护', at_sender=True)
            return
        uid = str(ev.message[0].data['qq'])
    elif len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = str(ev['user_id'])

    while not lck.locked():
        with lck:
            if not uid in binds:
                await bot.finish(ev, '未绑定竞技场', at_sender=True)
                return

            binds.pop(uid)
            save_binds()

            await bot.finish(ev, '删除竞技场订阅成功', at_sender=True)
        break

@sv.on_fullmatch('竞技场状态')
async def send_arena_sub_status(bot,ev):
    global binds, lck
    uid = str(ev['user_id'])

    while not lck.locked():
        with lck:
            if not uid in binds:
                await bot.send(ev,'您还未绑定竞技场', at_sender=True)
            else:
                info = binds[uid]
                await bot.finish(ev,
                f'''
                当前竞技场绑定ID：{info['id']}
                竞技场订阅：{'开启' if info['arena_on'] else '关闭'}
                公主竞技场订阅：{'开启' if info['grand_arena_on'] else '关闭'}''',at_sender=True)
        break

@sv.scheduled_job('interval', minutes=2)
async def on_arena_schedule():
    global cache, binds, lck
    bot = get_bot()
    
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    now = utc_now.astimezone(SHA_TZ)
    hour = now.hour
    
    while not lck.locked():
        with lck:
            for user in binds:
                if hour < 10:
                    continue
                #过滤失效的ID
                if not binds[user]['private']:
                    continue
                info = binds[user]
                try:
                    res = await query(info['id'])
                    res = (res['arena_rank'], res['grand_arena_rank'])

                    if user not in cache:
                        cache[user] = res
                        continue

                    last = cache[user]
                    cache[user] = res

                    if res[0] > last[0] and info['arena_on']:
                        await bot.send_group_msg(
                            group_id = int(binds[user]['gid']),
                            message = f'[CQ:at,qq={user}]您的竞技场排名发生变化：{last[0]}->{res[0]}'
                        )

                    if res[1] > last[1] and info['grand_arena_on']:
                        await bot.send_group_msg(
                            group_id = int(binds[user]['gid']),
                            message = f'[CQ:at,qq={user}]您的公主竞技场排名发生变化：{last[1]}->{res[1]}'
                        )
                except Exception as e:
                    sv.logger.info(f'对{binds[user]["id"]}的检查出错\n{e}')
                    if not '维护' in str(e):
                        binds[user]['private'] = False
                        save_binds()
        break

@sv.on_notice('group_decrease.leave')
async def leave_notice(session: NoticeSession):
    global lck, binds
    uid = str(session.ctx['user_id'])
    while not lck.locked():
        with lck:
            if uid in binds:
                binds.pop(uid)
                save_binds()
        break
