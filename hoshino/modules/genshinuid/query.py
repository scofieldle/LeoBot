import json
import time
import string
import random
import hashlib
from hoshino import aiorequests
from . import util
from urllib.parse import urlencode

mhyVersion = "2.11.1"
    
def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()

def __get_ds__(query, body=None):
    if body:
        body = json.dumps(body)
    n = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs" # Github-@lulu666lulu
    i = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    q = '&'.join([f'{k}={v}' for k, v in query.items()])
    c = __md5__("salt=" + n + "&t=" + i + "&r=" + r + '&b=' + (body or '') + '&q=' + q)
    return i + "," + r + "," + c

async def info(uid, cookie):
    server = 'cn_gf01'
    if uid[0] == "5":
        server = 'cn_qd01'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        "User-Agent":
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1",
        "Referer": "https://webstatic.mihoyo.com/",
        "x-rpc-app_version": "2.11.1",
        "x-rpc-client_type": '5',
        "DS": "",
        'Cookie': cookie
    }

    params = {"role_id": uid, "server": server}

    api = 'index'
    json_data = None
    fn = aiorequests.get
    base_url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/%s'
    url = base_url % api + '?'
    url += urlencode(params)

    headers['DS'] = __get_ds__(params, json_data and json.dumps(json_data, separators=(',', ':')))
    req = await fn(url=url, headers=headers, json=json_data)
    if req:
        return util.dict_to_object(json.loads(await req.text))
    else:
        return


class stats:
    def __init__(self, data, max_hide=False):
        self.data = data
        self.max_hide = max_hide

    @property
    def active_day(self) -> int:
        return self.data['active_day_number']

    @property
    def active_day_str(self) -> str:
        return '活跃天数: %s' % self.active_day

    @property
    def achievement(self) -> int:
        return self.data['achievement_number']

    @property
    def achievement_str(self) -> str:
        return '成就达成数: %s' % self.achievement

    @property
    def anemoculus(self) -> int:
        return self.data['anemoculus_number']

    @property
    def anemoculus_str(self) -> str:
        if self.max_hide and self.anemoculus == 66:
            return ''
        return '风神瞳: %s/66' % self.anemoculus

    @property
    def geoculus(self) -> int:
        return self.data['geoculus_number']

    @property
    def geoculus_str(self) -> str:
        if self.max_hide and self.geoculus == 131:
            return ''
        return '岩神瞳: %s/131' % self.geoculus

    @property
    def avatar(self) -> int:
        return self.data['avatar_number']

    @property
    def avatar_str(self) -> str:
        return '获得角色数: %s' % self.avatar

    @property
    def way_point(self) -> int:
        return self.data['way_point_number']

    @property
    def way_point_str(self) -> str:
        if self.max_hide and self.way_point == 83:
            return ''
        return '解锁传送点: %s/83' % self.way_point

    @property
    def domain(self) -> int:
        return self.data['domain_number']

    @property
    def domain_str(self) -> str:
        return '解锁秘境: %s' % self.domain

    @property
    def spiral_abyss(self) -> str:
        return self.data['spiral_abyss']

    @property
    def spiral_abyss_str(self) -> str:
        return '' if self.spiral_abyss == '-' else '当期深境螺旋: %s' % self.spiral_abyss

    @property
    def common_chest(self) -> int:
        return self.data['common_chest_number']

    @property
    def common_chest_str(self) -> str:
        return '普通宝箱: %s' % self.common_chest

    @property
    def exquisite_chest(self) -> int:
        return self.data['exquisite_chest_number']

    @property
    def exquisite_chest_str(self) -> str:
        return '精致宝箱: %s' % self.exquisite_chest

    @property
    def luxurious_chest(self) -> int:
        return self.data['luxurious_chest_number']

    @property
    def luxurious_chest_str(self) -> str:
        return '华丽宝箱: %s' % self.luxurious_chest

    @property
    def precious_chest(self) -> int:
        return self.data['precious_chest_number']

    @property
    def precious_chest_str(self) -> str:
        return '珍贵宝箱: %s' % self.precious_chest

    @property
    def string(self):
        str_list = [
            self.active_day_str,
            self.achievement_str,
            self.anemoculus_str,
            self.geoculus_str,
            self.avatar_str,
            self.way_point_str,
            self.domain_str,
            self.spiral_abyss_str,
            self.luxurious_chest_str,
            self.precious_chest_str,
            self.exquisite_chest_str,
            self.common_chest_str
        ]
        return '\n'.join(list(filter(None, str_list)))