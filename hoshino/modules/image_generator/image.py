from os import path

from PIL import ImageFont, ImageDraw
import re
import aiohttp

imagepath = path.join(path.dirname(__file__), 'high_eq_image.png')
fontpath = path.join(path.dirname(__file__), 'NotoSansCJKSC-Black.ttf')


def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(fontpath, 48)
    width, height = draw.textsize(text, font)
    x = 5
    if width > 390:
        font = ImageFont.truetype(fontpath, int(390 * 48 / width))
        width, height = draw.textsize(text, font)
    else:
        x = int((400 - width) / 2)
    draw.rectangle((x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2), fill=(0, 0, 0, 255))
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))


async def get_jl(index, jl, px, bottom):
    data = {
        'id': jl,
        'zhenbi': '20191123',
        'id2': '18',
        'id5': '10',
        'id7': bottom,
    }
    if index == '盘旋':
        subfix = '111'
        data['id1'] = '9007'
        data['id3'] = '#0000FF'
        data['id4'] = '#FF0000'
        data['id8'] = '9005'
        data['id10'] = px
        data['id11'] = 'jiqie.com_2'
        data['id12'] = '241'
    elif index == '飞升':
        subfix = '111'
        data['id1'] = '9005'
        data['id3'] = '#00FF00'
        data['id4'] = '#FFFF00'
        data['id8'] = '9008'
        data['id10'] = px
        data['id11'] = 'jiqie.com_1'
        data['id12'] = '505'
    elif index == '酷炫':
        subfix = '102'
        data['id1'] = '9005'
        data['id3'] = '#CDE374'
        data['id4'] = '#4CA3CF'
        data['id8'] = '9007'
    else: return None
    async with aiohttp.request(method='POST', url=f"http://jiqie.zhenbi.com/e/re{subfix}.php", data=data) as resp:
        t = await resp.text()
        regex = '<img src="(.+)">'
        return re.match(regex, t).groups()[0]
