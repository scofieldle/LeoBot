from nonebot import *
from . import query, util
from hoshino import Service  # 如果使用hoshino的分群管理取消注释这行
from hoshino.util import pic2b64
from nonebot import MessageSegment
import requests, os
from PIL import Image

#
sv = Service('ys-user')  # 如果使用hoshino的分群管理取消注释这行
# 初始化配置文件
config = util.get_config()

# 初始化nonebot
_bot = get_bot()

db = util.init_db(config.cache_dir)
cookie_list = [config.a,config.b,config.c,config.d]

def zipPic(name):
    path = os.getcwd() + '/hoshino/modules/genshinuid/genshin_card/' + name + '.png'
    im = Image.open(path)
    # 获得图像尺寸:
    w, h = im.size
    # 算出缩小比
    Proportion = 4
    # 缩放
    im.thumbnail((w // Proportion, h // Proportion))
    return str(MessageSegment.image(pic2b64(im)))

@sv.on_message('group')  # 如果使用hoshino的分群管理取消注释这行 并注释下一行的 @_bot.on_message("group")
async def main(*params):
    bot, ctx = (_bot, params[0]) if len(params) == 1 else params
    uid = ctx.user_id
    msg = str(ctx['message']).strip()
    keyword = util.get_msg_keyword(config.comm.player_uid, msg, True)
    if isinstance(keyword, str):
        if not keyword:
            info = db.get(uid, {})
            if not info:
                return await bot.send(ctx, '请在原有指令后面输入游戏uid,只需要输入一次就会记住下次直接使用%s获取就好' % config.comm.player_uid)
            else:
                keyword = info['uid']
        if not keyword.isdigit():
            await bot.send(ctx, '只能是数字ID啦')
            return

        await bot.send_group_forward_msg(group_id=ctx.group_id, messages=await get_stat(keyword))
        db[uid] = {'uid': keyword}


async def get_stat(uid):
    for cookie in cookie_list:
        info = query.info(uid, cookie)
        if info.retcode != 0:
            if '30' in info.message:
                continue
            else:
                data = {
                        "type": "node",
                        "data": {
                            "name": "妈",
                            "uin": "197812783",
                            "content":'[%s]错误或者不存在 (%s)' % (uid, info.message)
                                }
                            }
                return [data]
        else:
            break
    stats = query.stats(info.data.stats, True)
    msg = 'UID: %s\n%s\n' % (uid, stats.string)
    for i in info.data.world_explorations:
        msg += '\n%s的探索进度为%s，声望等级为：%s级' % (i["name"], str(i["exploration_percentage"] / 10) + '%', i["level"])
    msg +='\n\n好感度大于等于8的角色有：'
    for i in info.data.avatars:
        if i["fetter"] > 7:
            msg += f'\n{zipPic(i["name"])}{i["name"]},{i["level"]}级'
    data = {
            "type": "node",
            "data": {
                "name": "妈",
                "uin": "197812783",
                "content":msg
                    }
                }
    return [data]
