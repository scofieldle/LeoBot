import random,os,json
from hoshino import Service
from hoshino.typing import CQEvent
import hoshino
sv = Service('yiyunsentence', enable_on_default=True, visible=True,help_='''
[网抑云时间] 来点网抑云语录
'''.strip())

def get_nt_words():
    _path = os.path.join(os.path.dirname(__file__), 'nt_words.json')
    with open(_path,"r",encoding='utf-8') as dump_f:
        try:
            # 读取错误一般是人工改动了config并且导致json格式错误
            words = json.load(dump_f)
        except Exception as e:
            hoshino.logger.error(f'读取网抑云语录时发生错误{type(e)}')
            return None
    keys = list(words.keys())
    key = random.choice(keys)

    return words[key]["text"]


@sv.on_fullmatch(('网抑云时间','生而为人','生不出人','网抑云'))
async def net_ease_cloud_word(bot,ev:CQEvent):
    nt_word = get_nt_words()
    await bot.send(ev, nt_word, at_sender=True)