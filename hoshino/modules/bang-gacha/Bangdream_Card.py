import os
import time
import random
import csv

from PIL import Image
from hoshino import Service, R
from hoshino.typing import *
from hoshino.config import RES_DIR
from hoshino.util import FreqLimiter, DailyNumberLimiter, pic2b64, concat_pic



csvpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
picpath = os.path.join(os.path.expanduser(RES_DIR), 'img','bangdreampic')

sv_help = '''
[邦邦十连 (卡池编号)] 十连抽卡模拟，若未输入卡池编号则随机选取
[邦邦天井 (卡池编号)] 天井抽卡模拟
[查询邦邦卡池 (卡池编号)] 查询卡池信息
'''.strip()

sv = Service('bangdream-gacha', help_=sv_help)


EXCEED_NOTICE = f'您今天已经抽过10000星石了，请明早5点后再来~'
EXCEED_NOTICE2 = f'您今天已经抽过一井了，请明早5点后再来~'

_nlmt = DailyNumberLimiter(4)
_tlmt = DailyNumberLimiter(1)

_flmt = FreqLimiter(10)


def csv_to_dict(file_name):
    outdict={}
    flist = list(csv.reader(open(file_name,'r',encoding="utf-8")))
    for i in range(1,len(flist)):
        row=flist[i]
        outdict[row[0]]=row
    return outdict


card_dict = csv_to_dict(os.path.join(csvpath, 'bang_card.csv'))
pool_dict = csv_to_dict(os.path.join(csvpath, 'bang_pool.csv'))


def get_pool_by_date(poolid):

    poolinfo = pool_dict[poolid]
    pooltype = poolinfo[2]
    pooldate = poolinfo[4]
    poolstamp = int(time.mktime(time.strptime(pooldate, "%Y/%m/%d")))
    
    uplist=[[],[],[]]
    
    for i in range(5,len(poolinfo)):
        if poolinfo[i]:
            star=int(card_dict[poolinfo[i]][5])
            uplist[star-2].append(poolinfo[i])
    
    nlist=[[],[],[]]        

    for k in card_dict:
        card = card_dict[k]
        carddate = card[6]
        cardtype = card[7]
        star=int(card[5])
        cardstamp = int(time.mktime(time.strptime(carddate, "%Y/%m/%d")))
        if card[0] in uplist[star-2]:
            continue
        if cardstamp<poolstamp:
            if cardtype == "恒常カード":
                nlist[star-2].append(card[0])
            elif cardtype == "ドリフェス限定" and pooltype == "ドリームフェスティバル":
                nlist[star-2].append(card[0])
    return uplist, nlist


async def card_10(poolid="1"):
        
    uplist, nlist = get_pool_by_date(poolid)

    #fes池与普池概率确定
    poolinfo = pool_dict[poolid]
    pooltype = poolinfo[2]
    
    if pooltype=="ドリームフェスティバル":
        pup4 = 20
        pn4 = 40 + pup4 
        pup3 = 12 + pn4
        pn3 = 73 + pup3
        pup2 = 96 + pn3
        pn2 = 1000
    else:
        pup4 = 10
        pn4 = 20 + pup4 
        pup3 = 12 + pn4
        pn3 = 73 + pup3
        pup2 = 96 + pn3
        pn2 = 1000
        
    if uplist[2]==[]:
        pup4=0
    if uplist[1]==[]:
        pup3=pn4
    if uplist[0]==[]:
        pup2=pn3
    
    result = []
    upcount = 0
    count = 0

    #前九连
    for i in range(9):
        ran = random.uniform(0, 1000)
        if ran <= pup4:
            result.append(random.choice(uplist[2]))
            upcount += 1
            count += 1
        elif ran <= pn4:
            result.append(random.choice(nlist[2]))
            count += 1
        elif ran <= pup3:
            result.append(random.choice(uplist[1]))
        elif ran <= pn3:
            result.append(random.choice(nlist[1]))
        elif ran <= pup2:
            result.append(random.choice(uplist[0]))
        else:
            result.append(random.choice(nlist[0]))

    #保底
    ran = random.uniform(0, 1000)
    if ran <= pup4:
        result.append(random.choice(uplist[2]))
        upcount += 1
        count += 1
    elif ran <= pn4:
        result.append(random.choice(nlist[2]))
        count += 1
    elif ran <= pup3:
        result.append(random.choice(uplist[1]))
    else:
        result.append(random.choice(nlist[1]))
    
    base_img = Image.open(os.path.join(picpath, "Background.png"))
    
    box1 = (253, 175, 393, 315)
    for x in result[:5]:
        tmp_img = Image.open(os.path.join(picpath,"card",f"{x}_0.png")).resize((140, 140))
        tmp_img=tmp_img.convert('RGBA')
        r, g, b, a = tmp_img.split()
        base_img.paste(tmp_img, box1, mask=a)
        lst = list(box1)
        lst[0] += 157
        lst[2] += 157
        box1 = tuple(lst)
            
    box1 = (253, 330, 393, 470)
    for x in result[5:]:
        tmp_img = Image.open(os.path.join(picpath,"card",f"{x}_0.png")).resize((140, 140))
        tmp_img=tmp_img.convert('RGBA')
        r, g, b, a = tmp_img.split()
        base_img.paste(tmp_img, box1, mask=a)
        lst = list(box1)
        lst[0] += 157
        lst[2] += 157
        box1 = tuple(lst)
    
    return MessageSegment.image(pic2b64(base_img))



def card_300(poolid="1"):
        
    uplist, nlist = get_pool_by_date(poolid)

    #fes池与普池概率确定
    poolinfo = pool_dict[poolid]
    pooltype = poolinfo[2]
    
    if pooltype=="ドリームフェスティバル":
        pup4 = 20
        pn4 = 40 + pup4 
        pup3 = 12 + pn4
        pn3 = 73 + pup3
        pup2 = 96 + pn3
        pn2 = 1000
    else:
        pup4 = 10
        pn4 = 20 + pup4 
        pup3 = 12 + pn4
        pn3 = 73 + pup3
        pup2 = 96 + pn3
        pn2 = 1000
        
    if uplist[2]==[]:
        pup4=0
    if uplist[1]==[]:
        pup3=pn4
    if uplist[0]==[]:
        pup2=pn3
    
    result = []
    upcount = 0
    count = 0
    first_up_pos = 999999

    for k in range(30):

        for i in range(9):
            ran = random.uniform(0, 1000)
            if ran <= pup4:
                result.append(random.choice(uplist[2]))
                upcount += 1
                count += 1
                first_up_pos = min(first_up_pos, 10 * k + i+1)
            elif ran <= pn4:
                result.append(random.choice(nlist[2]))
                count += 1
            else:
                pass

        ran = random.uniform(0, 1000)
        if ran <= pup4:
            result.append(random.choice(uplist[2]))
            upcount += 1
            count += 1
            first_up_pos = min(first_up_pos, 10 * (k + 1))
        elif ran <= pn4:
            result.append(random.choice(nlist[2]))
            count += 1
        else:
            pass
        
    lenth = len(result)

    if lenth <= 0:
        res = "竟...竟然没有4★？！"
    else:
        step = 3 if lenth <= 9 else 4
        pics=[]
        for i in range(0, lenth, step):
            size=180
            j = min(lenth, i + step)
            des = Image.new('RGBA', (step*size, size), (255, 255, 255, 255))
            for k, card in enumerate(result[i:j]):
                src = Image.open(os.path.join(picpath,"card",f"{card}_0.png"))
                des.paste(src, (k * size, 0))
            pics.append(des)
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)
    
    return res, count, first_up_pos



async def tip(poolid="1"):
    poolinfo = pool_dict[poolid]
    pooltype = poolinfo[2]
    name = poolinfo[1]
    pic = pic2b64(Image.open(os.path.join(picpath,"pool",f"{poolid}.png")))
    pic = MessageSegment.image(pic)
    return f"卡池{poolid}[{name}]\n{pic}\n米歇尔祈愿中..."



@sv.on_prefix('邦邦十连')
async def bang_gacha(bot, ev):
    uid = ev['user_id']
    if not _tlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE2, at_sender=True)
        return
    if not _flmt.check(uid):
        await bot.send(ev, '麻里奈小姐忙不过来啦！', at_sender=True)
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)
    poolid = str(ev.message)
    if poolid in pool_dict:
        pass
    elif poolid=="":
        await bot.send(ev, '未指定卡池，随机选取卡池中……')
        poolid = random.choice(list(pool_dict.keys()))
    else:
        await bot.finish(ev, '没有对应的卡池哦')

    machinasai = await tip(poolid)
    await bot.send(ev, machinasai)
    pic = await card_10(poolid)
    result = f'{pic}'
    await bot.finish(ev, result)


@sv.on_prefix('邦邦天井')
async def bang_300(bot, ev):
    uid = ev['user_id']
    if not _nlmt.check(uid):
        await bot.send(ev, EXCEED_NOTICE, at_sender=True)
        return
    if not _flmt.check(uid):
        await bot.send(ev, '麻里奈小姐忙不过来啦！', at_sender=True)
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)
    poolid = str(ev.message)
    
    if poolid in pool_dict:
        pass
    elif poolid=="":
        await bot.send(ev, '未指定卡池，随机选取卡池中……')
        poolid = random.choice(list(pool_dict.keys()))
    else:
        await bot.finish(ev, '没有对应的卡池哦')

    machinasai = await tip(poolid)
    await bot.send(ev, machinasai)
    pic, count, first_up_pos = card_300(poolid)
    result = f'{pic}'
    await bot.send(ev, result)
    msg = f"获得4星共{count}个！\n第{first_up_pos}抽首次获得up角色！" if first_up_pos<300 else f"获得4星共{count}个！没有获得up角色……"
    await bot.send(ev, msg)


@sv.on_prefix('查询邦邦卡池')
async def bang_gacha(bot, ev):
    
    uid = ev['user_id']
    poolid = str(ev.message)
    
    if poolid in pool_dict:
        poolinfo = pool_dict[poolid]
        name = poolinfo[1]
        banner = pic2b64(Image.open(os.path.join(picpath,"pool",f"{poolid}.png")))
        banner = MessageSegment.image(banner)
        
        type = poolinfo[2]
        if type=="恒久的":
            type="普通"
        if type=="ドリームフェスティバル":
            type="Fes"
        
        start = poolinfo[3]
        end = poolinfo[4]
        uplist = poolinfo[5:]
        while "" in uplist:
            uplist.remove("")

        step = 3 if len(uplist)>=3 else 2
        pics=[]
        for i in range(0, len(uplist), step):
            size=180
            j = min(len(uplist), i + step)
            des = Image.new('RGBA', (step*size, size), (255, 255, 255, 255))
            for k, card in enumerate(uplist[i:j]):
                src = Image.open(os.path.join(picpath,"card",f"{card}_0.png"))
                des.paste(src, (k * size, 0))
            pics.append(des)
        res = concat_pic(pics)
        up=MessageSegment.image(pic2b64(res))

        msg=f"卡池[{name}]\n{banner}\n{type}池，开始于{start}，结束于{end}\nPickUp列表：{up}"
        await bot.finish(ev, msg)
    else:
        await bot.finish(ev, '没有对应的卡池哦')
