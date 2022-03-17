from nonebot import on_notice, NoticeSession
from hoshino import util

@on_notice('group_decrease.kick_me')
async def kick_me_alert(session: NoticeSession):
    group_id = session.event.group_id
    operator_id = session.event.operator_id
    coffee = session.bot.config.SUPERUSERS[0]
    util.GROUP_DB.delete(gid)
    await session.bot.send_private_msg(self_id=session.event.self_id, user_id=coffee, message=f'被Q{operator_id}踢出群{group_id}')
