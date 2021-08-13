from hoshino import Service, MessageSegment
from ..util import get_config
from . import query, info_card
from threading import Lock
import time

sv_help = '''
[ys#UID] 查询一个用户信息
'''.strip()

sv = Service(
    name='原神UID查询',  # 功能名
    help_=sv_help  # 帮助说明
)
config = get_config()
last_time = time.time()
lck = Lock()

@sv.on_prefix('ys#')
async def main(bot, ev):
    global lck, last_time
    now_time = time.time()
    uid = ev.message.extract_plain_text().strip()
    qid = ev.user_id
    nickname = ev['sender']['nickname']
    m = ev.message

    if not uid:
        await bot.finish(ev, '请在原有指令后面输入游戏uid,只需要输入一次就会记住下次直接使用{comm}获取就好\n例如:{comm}105293904'.format(comm='ys#'))

    if now_time - last_time < 5:
        await bot.send(ev, '请求过于频繁！')
        return

    while not lck.locked():
        with lck:
            if uid.isdigit() and (len(uid) == 9):
                try:
                    raw_data = await query.info(uid=uid)

                    if isinstance(raw_data, str):
                        await bot.finish(ev, raw_data)

                    if raw_data.retcode != 0:
                        await bot.finish(ev, f'{uid} 不存在,或者未在米游社公开.(请打开米游社,我的-个人主页-管理-公开信息)')
                except Exception as e:
                    print(e)
                    await bot.send(ev, 'cookie使用达到上限或米游社无法查询到此uid')
                    last_time = time.time()
                    return

                im = await info_card.draw_info_card(uid=uid, qid=qid, nickname=nickname, raw_data=raw_data.data)
                data = {"type": "node","data": {"name": "妈","uin": "197812783","content": MessageSegment.image(im)}}
                await bot.send_group_forward_msg(group_id=ev['group_id'], messages=[data])
                query.save_uid_by_qid(qid, uid)
                last_time = time.time()
            else:
                await bot.send(ev, 'UID输入有误！', at_sender=True)
        break
