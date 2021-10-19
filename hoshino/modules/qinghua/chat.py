import json, time, os, random

from hoshino.typing import CQEvent, HoshinoBot
from hoshino import Service
from hoshino.util import FreqLimiter

sv = Service('qinghua')

_chat_flmt = FreqLimiter(3)
_chat_flmt_notice = ["慢...慢一..点❤", "冷静1下", "歇会歇会~~"]
file_name = "kimo.json"
file_path = os.path.join(os.path.dirname(__file__),file_name)

def _load_data():
    with open(file_path, "r", encoding="utf-8") as r:
        data = json.loads(r.read())
    return data
data = _load_data()

@sv.on_message()
async def chat(bot: HoshinoBot, ev: CQEvent):
    global data
    msg = ev.raw_message
    user_id = ev.user_id
    if not '197812783' in msg:
        return
    msg = msg.split('] ')[1]
    if not _chat_flmt.check(user_id):
        await bot.send(ev, random.choice(_chat_flmt_notice), at_sender = True)
        time.sleep(1)
        return
    _chat_flmt.start_cd(user_id)
    
    temp = ''
    if msg in data.keys():
        temp = random.choice(data[msg])
    else:
        for key in data.keys():
            if key in msg:
                temp = random.choice(data[msg])
    if temp:
        await bot.send(ev, temp, at_sender = True)

