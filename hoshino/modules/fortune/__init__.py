import pickle
from os import path, listdir
from random import choice

from PIL import Image
from aiocqhttp.message import MessageSegment

from hoshino import Service
from hoshino.typing import HoshinoBot, CQEvent
from hoshino.util import DailyNumberLimiter,pic2b64
from .data_source import drawing, load_config
from .good_luck import GOOD_LUCK

sv_help = '''
[抽签|人品|运势|占卜]
随机角色预测今日运势
准确率高达114.514%！
选签pcr|选签vtb|选签mix
'''.strip()
sv = Service('运势',help_=sv_help, bundle='pcr娱乐')
_lmt = DailyNumberLimiter(1)
_divines = {}

@sv.on_fullmatch(('抽签', '运势', '占卜', '人品'))
async def divine(bot: HoshinoBot, ev: CQEvent):
    global _divines
    uid = ev.user_id
    if not _lmt.check(uid):
        await bot.finish(ev, f'您今天抽过签了，再给您看一次哦{_divines[uid]}')
    
    _lmt.increase(uid)

    option = 'pcr'

    base_dir = path.join(path.dirname(__file__), 'data', option)
    img_dir = path.join(base_dir, 'img')
    copywriting = load_config(path.join(base_dir, 'copywriting.json'))
    copywriting = choice(copywriting['copywriting'])

    if copywriting.get('type'): # 有对应的角色文案
        luck_type = choice(copywriting['type'])
        good_luck = luck_type['good-luck']
        content = luck_type['content']
        title = GOOD_LUCK[good_luck]
        chara_id = choice(copywriting['charaid'])
        img_name = f'frame_{chara_id}.jpg'
    else:
        good_luck = copywriting.get('good-luck')
        content = copywriting.get('content')
        title = GOOD_LUCK[good_luck]
        img_name = choice(listdir(img_dir))
        

    # 添加文字
    img = Image.open(path.join(img_dir, img_name))
    title_font_path = path.join(path.dirname(__file__),  'font', 'Mamelon.otf')
    text_font_path = path.join(path.dirname(__file__),  'font', 'sakura.ttf')
    img = drawing(img, title, content, title_font_path, text_font_path)

    b64_str = pic2b64(img)
    pic = MessageSegment.image(b64_str)
    _divines[uid] = pic
    await bot.send(ev, pic)







