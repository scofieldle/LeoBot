import hoshino, os, json

from . import RSS_class, rsshub
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('twitter_spider', bundle='twitter订阅', help_='''
添加订阅 订阅名 RSS地址(/twitter/user/username)
删除订阅 订阅名
查看所有订阅
'''.strip())

hoshino_path = './hoshino/modules/CQTwitter/'

def load_config():
    try:
        config_path = hoshino_path + 'twitter_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf8') as config_file:
                return json.load(config_file)
        else:
            return {}
    except:
        return {}

def save_config(config):
    try:
        with open(hoshino_path + 'twitter_config.json', 'w', encoding='utf8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
        return True
    except:
        return False

async def spider_work(rss, bot):
    updates = await rsshub.getRSS(rss)
    if not updates:
        print(f'{rss.url}未检索到新推文')
        return
    print(f'{rss.url}检索到{len(updates)}个新推文！')

    for gid in rss.gid:
        await bot.send_group_forward_msg(group_id=gid, messages=updates)
            
@sv.on_prefix('添加订阅')
async def handle_RssAdd(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    s = ev.message.extract_plain_text().split(' ')
    try:
        name = s[0]
        url = s[1]
    except:
        await bot.send(ev, '输入参数缺失！')
        return

    config = load_config()
    gid = str(ev.group_id)
    if url in config.keys():
        if gid not in config[url].keys():
            config[url][gid] = name
        else:
            await bot.finish(ev, '此群已经添加过该订阅，请勿重复添加')
    else:
        config[url] = {}
        config[url][gid] = name
    
    if save_config(config):
        await bot.send(ev, f'添加订阅"{s}"成功!')
        # 重新加载缓存
        await twitter_search_spider()
    else:
        await bot.send(ev, '添加订阅失败，请重试')

@sv.on_prefix('删除订阅')
async def handle_RssDel(bot, ev: CQEvent):
    config = load_config()
    s = ev.message.extract_plain_text()
    gid = str(ev.group_id)
    for url in config.keys():
        if gid in config[url].keys():
            if s == config[url][gid]:
                config[url].pop(gid)
                msg = f'删除订阅"{s}"成功'
                if not save_config(config):
                    await bot.finish(ev, '删除订阅失败，请重试')
                await bot.send(ev, msg)
                return
    msg = f'删除失败, 此群未设置订阅"{s}"'
    await bot.send(ev, msg)
    
@sv.on_fullmatch('查看所有订阅')
async def handle_RssLook(bot, ev: CQEvent):
    config = load_config()
    gid = str(ev.group_id)
    msg = '' 
    for url in config.keys():
        if gid in config[url].keys():
            msg = msg + '\n' + config[url][gid] + ': ' + url
    if msg == '':
        msg = '此群还未添加twitter订阅'
    else:
        msg = 'twitter爬虫已开启!\n此群设置的订阅为:'  + msg
    await bot.send(ev, msg)

@sv.scheduled_job('interval',minutes=5)
async def twitter_search_spider():
    bot = hoshino.get_bot()
    config = load_config()
    for url in config.keys():
        gid = config[url].keys()
        if gid:
            rss = RSS_class.rss()
            rss.url = url
            rss.gid = gid
            await spider_work(rss, bot)
    for root, dirs, files in os.walk(hoshino_path):
        for name in files:
            if name.endswith('.jpg') or name.endswith('.png'):
                os.remove(os.path.join(root, name))
    