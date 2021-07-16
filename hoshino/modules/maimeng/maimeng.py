import os,random,requests
from nonebot.exceptions import CQHttpError
from hoshino.typing import NoticeSession
from hoshino import R, Service
from hoshino.util import FreqLimiter, DailyNumberLimiter
from PIL import Image
from io import BytesIO

_max = 5
EXCEED_NOTICE = f'一天戳{_max}次还不够吗？！'
_nlmt = DailyNumberLimiter(_max)
_flmt = FreqLimiter(3)

sv = Service('maimeng')
maimeng_folder = R.img('maimeng/').path

def maimeng_gener():
    while True:
        filelist = os.listdir(maimeng_folder)
        random.shuffle(filelist)
        for filename in filelist:
            if 'jpg' in filename or 'png' in filename:
                yield R.img('maimeng/', filename)

maimeng_gener = maimeng_gener()

def get_maimeng():
    return maimeng_gener.__next__()


@sv.on_notice('notify.poke')
async def maimeng(session: NoticeSession):
    uid = session.ctx['user_id']
    guid = session.ctx['group_id']
    at_id = str(session.ctx['target_id'])
    if at_id != '197812783':
        return
    if not _nlmt.check(uid):
        await session.send(EXCEED_NOTICE)
        return
    if not _flmt.check(uid):
        await session.send(f'太快了啦，人家也要时间准备的{uid}')
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)

    # conditions all ok, send a maimeng.
    pic = get_maimeng()
    try:
        await session.send(pic.cqcode)
    except CQHttpError:
        sv.logger.error(f"发送图片{pic.path}失败")
        try:
            await session.send(f'啊嘞，好像发送失败了')
        except:
            pass

def download_meme(url:str, file_name:str): 
    try:
        rsp = requests.get(url, stream=True, timeout=5)
        save_path = '/home/ubuntu/HoshinoBot/res/img/maimeng/' + file_name + '.jpg'
    except Exception as e:
        print(e)
        return ""
    if 200 == rsp.status_code:
        img = Image.open(BytesIO(rsp.content))
        img.save(save_path)
        return save_path
    else:
        return ""
        
@sv.on_prefix(('上传卖萌'))
async def upload_meme(bot,event):
    msg = event.message.extract_plain_text().split(" ")
    meme_name = ''.join(e for e in msg[0] if e.isalnum())
    for seg in event.message:
        if (seg.type == 'image'):
            meme_path = download_meme(seg.data['url'], meme_name)
            if (meme_path == ""):
                await bot.send(event,f'上传卖萌"{meme_name}"失败',at_sender=True)
                return
            await bot.send(event,f'上传卖萌"{meme_name}"成功',at_sender=True)
            