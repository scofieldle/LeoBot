import json

import hoshino
from hoshino import Service, priv
from hoshino import aiorequests
from hoshino.util import FreqLimiter

flmt = FreqLimiter(5)
sv = Service(
    name='疫情出行政策',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # False隐藏
    enable_on_default=True,  # 是否默认启用
)


# ============================================ #

async def get_policy(_from, to):
    url_city_list = 'https://r.inews.qq.com/api/trackmap/citylist?'
    city_list_raw = await aiorequests.get(url_city_list)
    city_list = await city_list_raw.json()
    msg = ""
    if city_list['status'] == 0 and city_list['message'] == "success":
        for province in city_list['result']:
            for city in province['list']:
                if _from == city['name']:
                    _from_id = city['id']
                if to == city['name']:
                    to_id = city['id']
    else:
        msg += "城市列表请求错误"
        return msg

    try:
        url_get_policy = f"https://r.inews.qq.com/api/trackmap/citypolicy?&city_id={_from_id},{to_id}"
    except UnboundLocalError:
        msg += "城市名错误"
        return msg

    policy_raw = await aiorequests.get(url_get_policy)
    policy = await policy_raw.json()
    if policy['status'] == 0 and policy['message'] == "success":
        data_leave = policy['result']['data'][0]
        data_to = policy['result']['data'][1]
        msg += f"{_from}离开政策：\n{data_leave['leave_policy'].strip()}（于{data_leave['leave_policy_date']}更新）"
        msg += "\n"
        msg += f"{to}进入政策：\n{data_to['back_policy'].strip()}（于{data_to['back_policy_date']}更新）"
        msg += "\n"
        msg += f"{to}酒店政策：\n{data_to['stay_info'].strip()}"
        msg += "\n"
        msg += "免责声明：以上所有数据来源于https://news.qq.com/hdh5/sftravel.htm#/"
    else:
        msg += "政策请求错误"
    return msg


def render_forward_msg(msg_list: list, uid=197812783, name='bot'):
    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
            "type": "node",
            "data": {
                "name": str(name),
                "uin": str(uid),
                "content": msg
            }
        })
    return forward_msg


@sv.on_prefix("出行政策")
async def travelpolicy(bot, ev):
    # 冷却器检查
    if not flmt.check(ev['user_id']):
        await bot.send(ev, f"出行政策查询冷却中，请{flmt.left_time(ev['user_id'])}秒后再试~", at_sender=True)
        return

    if len(ev.message.extract_plain_text().split()) == 0:
        await bot.send(ev, "\n请按照\n出行政策 出发地 目的地\n或\n出行政策 城市名\n的格式输入", at_sender=True)
        return
    elif len(ev.message.extract_plain_text().split()) == 1:
        _from = to = ev.message.extract_plain_text().split()[0]
    else:
        _from, to = ev.message.extract_plain_text().split()
        if _from == to:
            await bot.send(ev, "搁这儿原地tp呢")

    msg = await get_policy(_from, to)
    flmt.start_cd(ev['user_id'])
    if "错误" in msg:
        await bot.send(ev, msg, at_sender=True)
        return
    li = []
    for i in msg.split("\n"):
        i = i.strip()
        li.append(i)
    bot_info = await bot.get_login_info()
    bot_name = bot_info['nickname']
    forward_msg = render_forward_msg(li, uid=ev.self_id, name=bot_name)
    await bot.send_group_forward_msg(group_id=ev.group_id, messages=forward_msg)
    