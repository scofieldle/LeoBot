# coding=utf-8
from .processData import *
from hoshino import Service
from hoshino.typing import CQEvent

sv = Service("雀魂信息查询")
help_txt = '''这是一个HoshinoBot的雀魂查询相关插件
本插件数据来源于雀魂牌谱屋:https://amae-koromo.sapk.ch/
项目地址：https://github.com/DaiShengSheng/Majsoul_bot
由于牌谱屋不收录铜之间以及银之间牌谱，故所有数据仅统计2019年11月29日后金场及以上场次的数据

查询指令：
雀魂信息/雀魂查询 (金/金之间/金场/玉/王座) 昵称：查询该ID在金/玉/王座之间的详细数据
三麻信息/三麻查询 (金/金之间/金场/玉/王座) 昵称：查询该ID在三麻金/玉/王座之间的详细数据
雀魂牌谱 昵称：查询该ID下最近五场的对局信息
三麻牌谱 昵称：查询该ID下最近五场的三麻对局信息
'''

@sv.on_fullmatch("雀魂帮助")
async def help(bot, ev):
    await bot.send(ev, help_txt)

@sv.on_prefix(('雀魂信息','雀魂查询'))
async def majsoulInfo(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    if len(args) == 1:
        nickname = ev.message.extract_plain_text()
        message = "\n"
        IDdata = getID(nickname)
        sv.logger.info("正在查询" + nickname + "的对局数据")
        if IDdata == -1:
            await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(IDdata)>1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n\n"
                message = message + printBasicInfo(IDdata[0],"0","4")
                await bot.send(ev, message, at_sender=True)
            else:
                message = message+printBasicInfo(IDdata[0],"0","4")
                await bot.send(ev,message,at_sender=True)
    elif len(args) == 2:
        nickname = args[1]
        sv.logger.info("正在查询" + nickname + "的对局数据")
        message = "\n"
        room_level = ""
        if args[0] == "金场" or args[0] == "金" or args[0] == "金之间":
            room_level = "1"
        elif args[0] == "玉场" or args[0] == "玉" or args[0] == "玉之间":
            room_level = "2"
        elif args[0] == "王座" or args[0] == "王座之间":
            room_level = "3"
        else:
            await bot.finish(ev, "房间等级输入不正确，请重新输入",at_sender=True)
        IDdata = getID(nickname)
        if IDdata == -1:
            await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(IDdata) > 1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
                message = message + printExtendInfo(IDdata[0], room_level,"4")
                await bot.send(ev, message, at_sender=True)
            else:
                pic = printExtendInfo(IDdata[0], room_level,"4")
                await bot.send(ev, pic, at_sender=True)
    else:
        await bot.finish(ev, "查询信息输入不正确，请重新输入", at_sender=True)


@sv.on_prefix(('雀魂牌谱','牌谱查询'))
async def RecordInfo(bot, ev: CQEvent):
    nickname = ev.message.extract_plain_text()
    IDdata = getID(nickname)
    message = "\n"
    sv.logger.info("正在查询" + nickname + "的牌谱数据")
    if IDdata == -1:
        await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
    else:
        if len(IDdata) > 1:
            message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
            message = message + printRecordInfo(IDdata[0],4)
            await bot.send(ev, message, at_sender=True)
        else:
            message = message + printRecordInfo(IDdata[0],4)
            await bot.send(ev, message, at_sender=True)

@sv.on_prefix(('三麻信息','三麻查询'))
async def majsoulInfo(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    if len(args) == 1:
        nickname = ev.message.extract_plain_text()
        message = "\n"
        sv.logger.info("正在查询" + nickname + "的对局数据")
        IDdata = gettriID(nickname)
        if IDdata == -1:
            await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(IDdata)>1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n\n"
                message = message + printBasicInfo(IDdata[0],"0","3")
                await bot.send(ev, message, at_sender=True)
            else:
                message = message + printBasicInfo(IDdata[0],"0","3")
                await bot.send(ev,message,at_sender=True)
    elif len(args) == 2:
        nickname = args[1]
        sv.logger.info("正在查询" + nickname + "的对局数据")
        message = "\n"
        room_level = ""
        if args[0] == "金场" or args[0] == "金" or args[0] == "金之间":
            room_level = "1"
        elif args[0] == "玉场" or args[0] == "玉" or args[0] == "玉之间":
            room_level = "2"
        elif args[0] == "王座" or args[0] == "王座之间":
            room_level = "3"
        else:
            await bot.finish(ev, "房间等级输入不正确，请重新输入",at_sender=True)
        sv.logger.info("正在查询" + nickname + "的对局数据")
        IDdata = gettriID(nickname)
        if IDdata == -1:
            await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(IDdata) > 1:
                message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
                message = message + printExtendInfo(IDdata[0], room_level,"3")
                await bot.send(ev, message, at_sender=True)
            else:
                pic = printExtendInfo(IDdata[0], room_level,"3")
                await bot.send(ev, pic, at_sender=True)
    else:
        await bot.finish(ev, "查询信息输入不正确，请重新输入", at_sender=True)

@sv.on_prefix('三麻牌谱')
async def RecordInfo(bot, ev: CQEvent):
    nickname = ev.message.extract_plain_text()
    IDdata = gettriID(nickname)
    sv.logger.info("正在查询" + nickname + "的牌谱数据")
    message = "\n"
    if IDdata == -1:
        await bot.send(ev, "没有查询到该角色在金之间以上的对局数据呢~")
    else:
        if len(IDdata) > 1:
            message = message + "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称\n"
            message = message + printRecordInfo(IDdata[0],3)
            await bot.send(ev, message, at_sender=True)
        else:
            message = message + printRecordInfo(IDdata[0],3)
            await bot.send(ev, message, at_sender=True)
