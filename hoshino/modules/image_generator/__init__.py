from PIL import Image

from hoshino import Service, priv, logger, aiorequests
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import FreqLimiter, DailyNumberLimiter, pic2b64

from .generator import genImage
from .image import imagepath, draw_text, get_jl

lmt = DailyNumberLimiter(10)

HELP_MSG = '''
[UC震惊|uc震惊|震惊生成器] (上半句)|(下半句)
低情商 <文本> 高情商 <文本>
金龙盘旋 <文字1> <文字2> <底部文字>
金龙飞升 <文字1> <文字2> <底部文字>
金龙酷炫 <文字> <底部文字>
'''
sv = Service('生草图片生成器', help_=HELP_MSG)


@sv.on_prefix(('UC震惊', 'uc震惊', '震惊生成器'))
async def gen_5000_pic(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid = ev.message_id
    if not lmt.check(uid):
        await bot.send(ev, f'您今天已经使用过10次生成器了，休息一下明天再来吧~', at_sender=True)
        return
    try:
        keyword = ev.message.extract_plain_text().strip()
        if not keyword:
            await bot.send(ev, '请提供要生成的句子！')
            return
        if '｜' in keyword:
            keyword = keyword.replace('｜', '|')
        upper = keyword.split("|")[0]
        downer = keyword.split("|")[1]
        img = genImage(word_a=upper, word_b=downer)
        img = str(MessageSegment.image(pic2b64(img)))
        await bot.send(ev, img)
        lmt.increase(uid)
    except OSError:
        await bot.send(ev, '生成失败……请检查字体文件设置是否正确')
    except:
        await bot.send(ev, '生成失败……请检查命令格式是否正确')


@sv.on_rex('低情商(?P<left>.+)高情商(?P<right>.+)')
async def gen_high_eq(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    mid = ev.message_id
    left = ev['match'].group('left').strip()
    right = ev['match'].group('right').strip()

    if not lmt.check(uid):
        await bot.send(ev, f'您今天已经使用过10次生成器了，休息一下明天再来吧~', at_sender=True)
        return
    if len(left) > 15 or len(right) > 15:
        await bot.send(ev, '为了图片质量，请不要多于15个字符')
        return

    img_p = Image.open(imagepath)
    draw_text(img_p, left, 0)
    draw_text(img_p, right, 400)
    img = str(MessageSegment.image(pic2b64(img_p)))
    await bot.send(ev, img)
    lmt.increase(uid)


@sv.on_prefix('金龙')
async def gen_jl(bot, ev):
    uid = ev['user_id']
    gid = ev['group_id']
    mid = ev.message_id
    args = ev.message.extract_plain_text().split()

    if not lmt.check(uid):
        await bot.send(ev, f'您今天已经使用过10次生成器了，休息一下明天再来吧~', at_sender=True)
        return
    if args[0] == '盘旋':
        if len(args) != 4:
            await bot.send(ev, f"金龙{args[0]}需要三个参数")
            return
        else: url = await get_jl(args[0], args[1], args[2], args[3])
    elif args[0] == '飞升':
        if len(args) != 4:
            await bot.send(ev, f"金龙{args[0]}需要三个参数")
            return
        else: url = await get_jl(args[0], args[1], args[2], args[3])
    elif args[0] == '酷炫':
        if len(args) != 3:
            await bot.send(ev, f"金龙{args[0]}需要两个参数")
            return
        else: url = await get_jl(args[0], args[1], None, args[2])
    else: return
    
    try:
        img = str(MessageSegment.image(url))
        await bot.send(ev, img)
        lmt.increase(uid)
    except:
        bot.send(ev, '无法生成图片')

