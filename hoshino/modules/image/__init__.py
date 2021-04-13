from io import BytesIO
from hoshino import Service, priv
import os
from os import path
from .memeutil import draw_meme, download_meme
from PIL import Image
import base64
from . import get
from hoshino.util import pic2b64
from nonebot import MessageSegment

img_dir = path.join(path.abspath(path.dirname(__file__)),"meme/")
img = []
img_name = []
backImage = '/home/ubuntu/HoshinoBot/hoshino/modules/image/backImage.jpg'
sv_help = '''
[表情列表] 查看当前表情列表
[查看表情 <名字>] 查看指定表情
[生成表情 <名字> <文案>] 生成一张表情
[上传表情 <名字> <图片>] 上传一张表情
[删除表情 <名字>] 删除一张表情（仅限管理员）
'''.strip()

def load_images():
    global img,img_name,img_dir,backImage
    img = os.listdir(img_dir)
    res = Image.new('RGB', (500, 100* (int(len(img)/5)+1)), (255, 255, 255))
    i = 0
    j = 0
    for s in img:
        image = Image.open(os.path.join(img_dir,s))
        image=image.resize((100,100),Image.ANTIALIAS)
        res.paste(image, (i*100, j*100))
        i = i + 1
        if i > 4:
            i = 0
            j = j + 1
    res.save(backImage, format='JPEG')
    img_name = [''.join(s.split('.')[:-1]) for s in img]

load_images()

sv = Service('image',visible=True)

@sv.on_fullmatch(('表情帮助'))
async def img_help(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

@sv.on_prefix(('img','底图'))
async def switch_img(bot, ev):
    uid = ev.user_id
    msg = str(ev.message).strip()
    if msg in img_name:
        mark = get.setQqName(uid,msg)
        if mark != None:
            await bot.send(ev,f'表情已更换为{msg}', at_sender=True)
    else:
        await bot.send(ev,f'没有表情包{msg}', at_sender=True)

@sv.on_fullmatch(('表情列表','查看表情列表'))
async def show_memes(bot,ev):
    global backImage
    msg = "当前表情有："
    for meme in img_name:
        msg += "\n" + meme
    await bot.send(ev,msg,at_sender=True)
    res = str(MessageSegment.image(pic2b64(Image.open(backImage))))
    await bot.send(ev, res)

@sv.on_fullmatch(('更新表情','刷新表情','更新表情列表','刷新表情列表'))
async def reload_memes(bot,event):
    global img
    load_images()
    await bot.send(event,f"表情列表更新成功，现在有{len(img)}张表情")

@sv.on_prefix(('上传表情'))
async def upload_meme(bot,event):
	# if not priv.check_priv(event,priv.ADMIN):
	#     await bot.send(event, '该操作需要管理员权限', at_sender=True)
	#     return
	msg = event.message.extract_plain_text().split(" ")
	meme_name = ''.join(e for e in msg[0] if e.isalnum())
	for seg in event.message:
		if (seg.type == 'image'):
			meme_path = download_meme(seg.data['url'], meme_name)
			if (meme_path == ""):
				await bot.send(event,f'上传表情"{meme_name}"失败',at_sender=True)
			load_images()
			await bot.send(event,f'上传表情"{meme_name}"成功',at_sender=True)

@sv.on_prefix(('删除表情'))
async def remove_meme(bot,event):
	if not priv.check_priv(event,priv.ADMIN):
		await bot.send(event, '该操作需要管理员权限', at_sender=True)
		return
	msg = event.message.extract_plain_text().split(" ")
	meme_name = msg[0]
	if meme_name not in img_name:
		await bot.send(event,f'没有找到表情"{meme_name}"',at_sender=True)
		return

	idx = img_name.index(meme_name)
	file_path = os.path.join(img_dir,img[idx])
	if os.path.exists(file_path):
		os.remove(file_path)
		await bot.send(event,f'删除表情"{meme_name}"成功',at_sender=True)
	else:
		await bot.send(event,f'表情文件"{meme_name}"不存在',at_sender=True)

	del img[idx],img_name[idx]

@sv.on_suffix(('.jpg'))
async def generate_img(bot, ev):
    msg = ev.message.extract_plain_text()
    uid = ev.user_id
    file = str(get.getQqName(uid)) + '.jpg'
    image = Image.open(os.path.join(img_dir,file))
    meme = draw_meme(image,msg)

    buf = BytesIO()
    meme.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ev, f'[CQ:image,file={base64_str}]')

@sv.on_prefix(('生成表情'))
async def generate_meme(bot,event):
    msg = event.message.extract_plain_text().split(" ")

    sel = msg[0]
    if sel not in img_name:
        await bot.send(event,f'没有找到表情"{sel}"',at_sender=True)
        return

    idx = img_name.index(sel)
    image = Image.open(os.path.join(img_dir,img[idx]))
    message = " ".join(msg[1:])
    message = message.replace("\r","\n")
    meme = draw_meme(image,message)

    buf = BytesIO()
    meme.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')
