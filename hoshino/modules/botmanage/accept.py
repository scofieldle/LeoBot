from nonebot import on_request, NoticeSession
from hoshino import Service
from hoshino.util import GROUP_DB

sv = Service('accept')

@on_request('group.invite')
async def accept(session: NoticeSession):
    group_id = session.event.group_id
    await session.approve()
    GROUP_DB.init_group(group_id)
    coffee = session.bot.config.SUPERUSERS[0]
    await session.bot.send_private_msg(self_id=session.event.self_id, user_id=coffee, message=f'被邀请入群{group_id}')

@sv.on_prefix('解锁群聊')
async def unlock(bot, ev):
    gid = ev.message.extract_plain_text()
    if GROUP_DB.exist(gid):
        GROUP_DB.unlock(gid)
        await bot.send(ev, f'已解锁群聊{gid}')
    else:
        GROUP_DB.init_group(gid)
        GROUP_DB.unlock(gid)
        await bot.send(ev, f'已解锁群聊{gid}')

@sv.on_prefix('锁定群聊')
async def lock(bot, ev):
    gid = ev.message.extract_plain_text()
    if GROUP_DB.exist(gid):
        GROUP_DB.lock(gid)
        await bot.send(ev, f'已锁定群聊{gid}')
    else:
        GROUP_DB.init_group(gid)
        await bot.send(ev, f'已锁定群聊{gid}')