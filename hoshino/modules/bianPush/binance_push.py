from json import load, dump
from nonebot import get_bot
from hoshino import Service
from threading import Lock
from os.path import dirname, join
from binance import Client
import time, signal
import pandas as pd
import cufflinks as cf
import plotly.io as pio
from nonebot import MessageSegment
from hoshino.priv import *

sv_help = '''
[币安查询 xxx] [币安价格 xxx] 查询币种当前美元价
[币安提醒 xxx 价格1 价格2] 设置币种价格提醒
[取消币安提醒 xxx] 取消币种价格提醒
[币安k线 xxx] 查看币种一日内k线图
[币安推送 xxx] 将指定币种加入推送队列，只有管理员才可以
[取消币安推送 xxx] 取消指定币种的推送
'''

sv = Service('币安',help_=sv_help, bundle='比特币查询')

@sv.on_fullmatch('币安帮助')
async def send_jjchelp(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'normal_bind' : {},
    'admin_bind' : {}
}

client = None
lck = Lock()

with open(config) as fp:
    root = load(fp)

with open(join(curpath, 'account.json')) as fp:
    key = load(fp)
    client = Client(api_key = key['api_key'], api_secret = key['secret_key'])

def save_binds():
    with open(config, 'w') as fp:
        dump(root, fp, indent=4)

@sv.on_prefix('币安提醒')
async def normal_bind(bot, ev):
    global root, lck, client
    
    message = ev.message.extract_plain_text().split(' ')
    if len(message) == 3 and message[1].isdigit() and message[2].isdigit():
        BTC = message[0].upper() + 'USDT'
        try:
            client.get_symbol_ticker(symbol = BTC)
        except:
            await bot.send(ev, '参数错误,请检查货币拼写', at_sender=True)
            return
            
        try:
            price1 = float(message[1])
            price2 = float(message[2])
        except:
            await bot.send(ev, '参数错误，需要指定货币和两个价格', at_sender=True)
            return
        with lck:
            if BTC in root['normal_bind'].keys():
                root['normal_bind'][BTC][str(ev['user_id'])] = {
                    'gid': str(ev['group_id']),
                    'price1': price1,
                    'price2': price2
                }
            else:
                root['normal_bind'][BTC] = {}
                root['normal_bind'][BTC][str(ev['user_id'])] = {
                    'gid': str(ev['group_id']),
                    'price1': price1,
                    'price2': price2
                }
            save_binds()
        await bot.send(ev, f'{BTC}提醒绑定成功', at_sender=True)
        return
    await bot.send(ev, '参数错误，需要指定货币和两个价格', at_sender=True)

@sv.on_prefix(('币安查询','币安价格'))
async def query_binance(bot, ev):
    global client
    BTC = ev.message.extract_plain_text().upper() + 'USDT'
    try:
        resp = '$' + str(client.get_symbol_ticker(symbol = BTC)['price'])
        msg = f'当前{BTC}价格为{resp}'
        await bot.send(ev, msg, at_sender= True)
    except:
        await bot.send(ev, '查询失败，请检查货币拼写', at_sender= True)
    
@sv.on_prefix('币安推送')
async def binance_push(bot,ev):
    global root, lck, client
    if not check_priv(ev, 20):
        await bot.send(ev, '您不是管理员')
        return
    BTC = ev.message.extract_plain_text().upper() +'USDT'
    try:
        client.get_symbol_ticker(symbol = BTC)
    except:
        await bot.send(ev, '参数错误,请检查货币拼写', at_sender=True)
        return
        
    with lck:
        if BTC in root['admin_bind'].keys():
            root['admin_bind'][BTC].append(str(ev['group_id']))
        else:
            root['admin_bind'][BTC] = [str(ev['group_id'])]
        save_binds()
    await bot.send(ev, f'{BTC}推送绑定成功', at_sender=True)

@sv.on_prefix('取消币安提醒')
async def remove_normal_bind(bot,ev):
    global root, lck
    uid = str(ev['user_id'])
    BTC = ev.message.extract_plain_text().upper() + 'USDT'
    
    if BTC in root['normal_bind'].keys() and uid in root['normal_bind'][BTC].keys():
        with lck:
            del root['normal_bind'][BTC][uid]
            save_binds()
        await bot.send(ev, f'成功取消{BTC}提醒', at_sender=True)
        return
    await bot.send(ev, f'参数错误或没有绑定{BTC}提醒', at_sender=True)

@sv.on_prefix('取消币安推送')
async def remove_admin_bind(bot,ev):
    global root, lck
    if not check_priv(ev, 20):
        await bot.send(ev, '您不是管理员')
        return
    gid = str(ev['group_id'])
    BTC = ev.message.extract_plain_text().upper() + 'USDT'
    
    if BTC in root['admin_bind'].keys() and gid in root['admin_bind'][BTC]:
        with lck:
            root['admin_bind'][BTC].remove(gid)
            save_binds()
        await bot.send(ev, f'成功取消{BTC}推送', at_sender=True)
        return
    await bot.send(ev, f'参数错误或没有绑定{BTC}推送', at_sender=True)

def timestamp_to_fomat(timestamp=None,format='%Y-%m-%d %H:%M:%S'):
    #默认返回当前格式化好的时间
    #传入时间戳的话，把时间戳转换成格式化好的时间，返回
    if timestamp:
        time_tuple = time.localtime(timestamp)
        res = time.strftime(format,time_tuple)
    else:
        res = time.strftime(format)#默认读取当前时间
    return res
    
async def draw_klines(BTC, length, path):
    global client
    resp = client.get_klines(symbol = BTC, interval = '5m', limit = length)
    df = pd.DataFrame(resp)
    # 剔除不需要的数据部分并更改列名
    df = df.drop(columns=[6, 7, 8, 9, 10, 11])
    df.columns=["opentime", "open", "high", "low", "close", "volume"]
    # 修改时间格式
    df["opentime"] = (df["opentime"]//100000).map(timestamp_to_fomat)
    df.set_index(["opentime"], drop=True)
    
    qf=cf.QuantFig(df,title=BTC,legend='top',name='GS')
    fig = qf.figure()
    pio.write_image(fig, path)
    
@sv.on_prefix('币安k线')
async def binance_klines(bot,ev):
    BTC = ev.message.extract_plain_text().upper() + 'USDT'
    path = '/home/ubuntu/HoshinoBot/hoshino/modules/bianPush/1.png' 
    await draw_klines(BTC, 288, path)
    data = {
        "type": "node",
        "data": {
            "name": "小冰",
            "uin": "2854196306",
            "content":MessageSegment.image(f'file:///{path}')
                }
            }
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=[data])
    

@sv.scheduled_job('interval', minutes=5)
async def binance_schedule():
    global root, lck, client
    bot = get_bot()
    normal_bind = {}
    admin_bind = {}

    with lck:
        normal_bind = root['normal_bind']
        admin_bind = root['admin_bind']

    #push
    price = {}
    for BTC in admin_bind.keys():
        resp = '$' + str(client.get_symbol_ticker(symbol = BTC)['price'])
        for gid in admin_bind[BTC]:
            if gid in price.keys():
                price[gid] += f'\n{BTC}的价格为{resp}'
            else:
                price[gid] = f'币安价格实时推送:\n{BTC}的价格为{resp}'
                
    for gid in price.keys():
        try:
            await bot.send_group_msg(group_id = int(gid), message = price[gid])
        except:
            with lck:
                for BTC in root['admin_bind'].keys():
                    if gid in root['admin_bind'][BTC]:
                        root['admin_bind'][BTC].remove(gid)
    
    #remind
    for BTC in normal_bind.keys():
        resp = float(client.get_symbol_ticker(symbol = BTC)['price'])
        for uid in normal_bind[BTC].keys():
            price1 = normal_bind[BTC][uid]['price1']
            price2 = normal_bind[BTC][uid]['price2']
            if max(price1,price2) < resp or min(price1,price2) > resp:
                try:
                    await bot.send_group_msg(
                        group_id = int(normal_bind[BTC][uid]['gid']),
                        message = f'[CQ:at,qq={uid}] {BTC}目前价格为${resp}'
                    )
                except:
                    with lck:
                        del root[normal_bind][BTC][uid]
                        save_binds()
                
    
    
    
    
    
    
    

