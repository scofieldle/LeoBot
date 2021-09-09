# coding=utf-8
from hoshino import Service
from hoshino.typing import HoshinoBot,CQEvent
from .Life import Life
from .PicClass import *
import traceback
import time
import random

sv = Service("人生重来模拟器")

def genp(prop):
    ps = []
    # for _ in range(4):
    #     ps.append(min(prop, 8))
    #     prop -= ps[-1]
    while True:
        for i in range(0,4):
            if i == 3:
                ps.append(prop)
            else:
                if prop>=10:
                    ps.append(random.randint(0, 10))
                else:
                    ps.append(random.randint(0, prop))
                prop -= ps[-1]
        if ps[3]<10:
            break
        else:
            prop = 20
            ps.clear()
    return {
        'CHR': ps[0],
        'INT': ps[1],
        'STR': ps[2],
        'MNY': ps[3]
    }

@sv.on_fullmatch(("/remake","人生重来"))
async def remake(bot,ev:CQEvent):
    Life.load(os.path.join(os.path.dirname(__file__), 'data'))
    life = Life()
    life.setErrorHandler(lambda e: traceback.print_exc())
    life.setTalentHandler(lambda ts: random.choice(ts).id)
    life.setPropertyhandler(genp)

    life.choose()

    choice = 0
    person = "你本次重生的基本信息如下：\n\n【你的天赋】\n"
    for t in life.talent.talents:
        choice = choice + 1
        person = person + str(choice) + "、天赋：【" + t.name + "】" + " 效果:" + t.desc + "\n"

    person = person + "\n【基础属性】\n"
    person = person + "   美貌值:" + str(life.property.CHR)+"  "
    person = person + "智力值:" + str(life.property.INT)+"  "
    person = person + "体质值:" + str(life.property.STR)+"  "
    person = person + "财富值:" + str(life.property.MNY)+"  "
    pic = ImgText(person)
    await bot.send(ev, "你的命运正在重启....")
    time.sleep(5)
    pic1 = await pic.draw_text()
    res = life.run()
    mes = '\n'.join('\n'.join(x) for x in res)
    pic = ImgText(mes)
    pic2 = await pic.draw_text()
    msg = []
    msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":pic1}})
    msg.append({"type": "node","data": {"name": "小冰","uin": "2854196306","content":pic2}})
    await bot.send_group_forward_msg(group_id=ev.group_id, messages=msg)