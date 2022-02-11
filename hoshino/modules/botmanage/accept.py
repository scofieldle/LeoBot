from nonebot import on_request, NoticeSession
from hoshino import Service

sv = Service('accept')

group_list = []
hoshino_path = './hoshino/modules/botmanage/'
with open(hoshino_path + '1.txt','r',encoding='utf-8') as f:
    line = f.readline()
    while line:
        group = line.split(' ')[0]
        group_list.append(group)
        line = f.readline()

@on_request('group.invite')
async def accept(session: NoticeSession):
    group_id = session.event.group_id
    print(group_id)
    if group_id in group_list:
        await session.approve()
    else:
        await session.reject(reason = '该群不在列表中')
        