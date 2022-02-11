# -*- coding: utf-8 -*-
from hoshino import Service, priv
from io import BytesIO
from PIL import Image
import base64, os

sv = Service('help', bundle='帮助')
msg = []
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"帕瑟芬妮bot功能表"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"dice:扔骰子。命令：.r (int i)d(int j)  抛i个最大为j的骰子"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"priconne：pcr相关功能。命令详情：pcr帮助"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"image：表情包生成器。命令：表情帮助"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"setu_mix：涩图模块，默认开启涩图撤回，默认关闭r18，暂停开放。命令：来x张涩图，搜涩图 xx"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"eclanrank：公会排名查询。命令：公会查询 xxx，排名查询 int，查询会长 xxx"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"yiyusentence：抑郁热评。命令：网抑云、网抑云时间"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"clanbattle_report 命令：会战报告(@xxx)；离职报告(@xxx) 如需使用请联系开发者报api"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"nowtime：命令：报时"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"memberguess 命令：猜群友"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"total_guess：命令：猜一猜、猜原神、猜干员、猜明日方舟、猜角色、猜pcr、猜公主连结"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"Genshin_Impact_bot：原神插件。命令：原神帮助"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"bang-gacha：邦邦抽卡。命令：邦邦天井 [int]；邦邦十连 [int]"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"weather：天气查询。命令：天气 xx | 查天气 xx"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"zhihu：知乎热词。命令：知乎、知乎日报"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"eqa：简易问答设定。命令：我问xxx你答xxx、删除问题xxx、不要回答xxx"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"bilpush：B站动态订阅。命令：订阅动态 UID、取消订阅动态 UID"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"rua：搓头像。命令：rua@xxx,、搓@xxx"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"BandoriStation：邦邦车站。命令：查询车站人数，ycm，有车吗"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"CP：土味情话生成。命令：cp x y"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"Majsoul_Info：雀魂信息查询。命令详情:雀魂帮助"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"maimeng：戳一戳机器人，随机返回表情包。 命令：上传卖萌 名字 表情包"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"pixiv：p站插画插件。命令详情:插画帮助"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"akgacha：明日方舟相关功能。命令详情:方舟帮助"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"bianpush：币安插件。命令详情：币安帮助"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"lifeRestart：命令：人生重来 /remake"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"music: 命令：点歌 xxx"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"qinghua: 情话插件，at bot 发送消息触发，关键词请自行摸索"}})
msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"bt_search: 命令：搜磁力 xxx | 聚合搜索 xxx"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"image_generator：uc震惊 上半句|下半句；低情商 上半句 高情商 下半句"}})
#msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"jinlong：金龙盘旋 文本1 文本2 底部文字；金龙炫酷 文本 底部文字"}})

battle_msg = []
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"会战功能列表"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"创建x服公会"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"加入公会(@xxx);加入全部成员"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"状态"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"报刀 xxxx (@xxx);报刀昨日 xxxx (@xxx)"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"尾刀 (@xxx);尾刀 昨日 (@xxx)"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"撤销"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"预约 x (留言)"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"预约表"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"挂树(:留言);可重复挂树覆盖留言"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"申请出刀;锁定 x 留言"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"取消预约 x"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"取消挂树"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"解锁"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"面板"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"sl (@xxx);sl? (@xxx)"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"查树"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"进度"}})
battle_msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"登录; 需要私聊bot"}})

FZ_help = []
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"@Bot方舟十连"}})
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"@Bot方舟来一井"}})
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"查看方舟卡池"}})
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"切换方舟卡池"}})
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"查看方舟历史卡池"}})
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"猜干员"}})
FZ_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"猜明日方舟"}})

pcr_help = []
pcr_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"calendar：日程表，激活后每日推送。命令：日程"}})
pcr_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"fortune 命令：抽签、运势"}})
pcr_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"jjc订阅：实时通知jjc、pjjc排名变动，命令：竞技场绑定 uid、竞技场查询、删除竞技场订阅"}})
pcr_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"pcrfind：找头像小游戏。命令：找头像"}})
pcr_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"yobot：yobot会战和web页面功能，详情私聊bot登录查看"}})

vedio_help = []
vedio_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"原神功能展示：https://b23.tv/1McXWWu"}})
vedio_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"猜一猜功能展示：https://b23.tv/TYx7I3J"}})
vedio_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"表情包、雀魂功能展示：https://b23.tv/7Sjb5Tu"}})
vedio_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"其他功能展示：https://b23.tv/VYncaJ5"}})#我问你答、订阅动态、rua、cp、人生重来、点歌、情话

update_help = []
update_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"更新方舟数据"}})
update_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"更新原神卡池"}})
update_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"更新原神地图"}})
update_help.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":"更新原神语音列表"}})

@sv.on_fullmatch('帮助')
async def help(bot, ev):
    global msg
    FILE_PATH = os.path.dirname(__file__)
    image = Image.open(os.path.join(FILE_PATH,'help.png'))
    bio = BytesIO()
    image.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes = f"[CQ:image,file={base64_str}]"
    #await bot.send_group_forward_msg(group_id=ev['group_id'], messages=msg)
    await bot.send(ev,mes)
    await bot.send(ev,"原神功能展示：https://b23.tv/1McXWWu")
    await bot.send(ev,"猜一猜功能展示：https://b23.tv/TYx7I3J")
    await bot.send(ev,"表情包、雀魂功能展示：https://b23.tv/7Sjb5Tu")
    await bot.send(ev,"其他功能展示：https://b23.tv/VYncaJ5")
    #await bot.send_group_forward_msg(group_id=ev['group_id'], messages=vedio_help)

@sv.on_fullmatch('会战帮助')
async def help(bot, ev):
    global battle_msg
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=battle_msg)
   
@sv.on_fullmatch('方舟帮助')
async def help(bot, ev):
    global FZ_help
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=FZ_help)
    
@sv.on_fullmatch('pcr帮助')
async def help(bot, ev):
    global pcr_help
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=pcr_help)

@sv.on_fullmatch('更新帮助')
async def help(bot, ev):
    global update_help
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev,'此命令仅维护组可用，请联系维护组~')
        return
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=update_help)