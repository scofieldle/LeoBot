import requests
from hoshino import Service
from nonebot import on_command

sv = Service('yiyusentence', enable_on_default=True, visible=True)

@sv.on_fullmatch(('网抑云时间'))
async def music163_sentences(bot, ev):
    resp = requests.get('http://api.heerdev.top/nemusic/random',timeout=30)
    if resp.status_code == requests.codes.ok:
        res = resp.json()
        sentences = res['text']
        await bot.send(ev, sentences, at_sender=True)
    else:
        await bot.send(ev, '上号失败，我很抱歉。您不pay被抑郁。', at_sender=True)