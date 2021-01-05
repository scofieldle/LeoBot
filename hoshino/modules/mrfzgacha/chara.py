import importlib, os
from io import BytesIO

import pygtrie
import requests
from fuzzywuzzy import fuzz, process
from PIL import Image
from nonebot import MessageSegment
from hoshino.util import pic2b64

import hoshino
from hoshino import R, log, sucmd, util
from hoshino.typing import CommandSession

from . import _data
from .config import *

logger = log.new_logger('chara', hoshino.config.DEBUG)
UNKNOWN = 1000

class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()
    
    def update(self):
        importlib.reload(_data)
        self._roster.clear()
        for idx, names in _data.CHARA_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
        self._all_name_list = self._roster.keys()


    def get_id(self, name):
        name = util.normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN


    def guess_id(self, name):
        """@return: id, name, score"""
        name, score = process.extractOne(name, self._all_name_list)
        return self._roster[name], name, score


    def parse_team(self, namestr):
        """@return: List[ids], unknown_namestr"""
        namestr = util.normalize_str(namestr)
        team = []
        unknown = []
        while namestr:
            item = self._roster.longest_prefix(namestr)
            if not item:
                unknown.append(namestr[0])
                namestr = namestr[1:].lstrip()
            else:
                team.append(item.value)
                namestr = namestr[len(item.key):].lstrip()
        return team, ''.join(unknown)


roster = Roster()

def name2id(name):
    return roster.get_id(name)

def fromid(id_, star=0, equip=0):
    return Chara(id_, star, equip)

def fromname(name, star=0, equip=0):
    id_ = name2id(name)
    return Chara(id_, star, equip)

def guess_id(name):
    """@return: id, name, score"""
    return roster.guess_id(name)

def gen_team_pic(team, size=64, star_slot_verbose=True):
    num = len(team)
    des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
    for i, chara in enumerate(team):
        src = chara.render_icon(size, star_slot_verbose)
        des.paste(src, (i * size, 0), src)
    return des


class Chara:

    def __init__(self, id_, star=0, equip=0):
        self.id = id_
        self.star = star
        self.equip = equip

    @property
    def name(self):
        return _data.CHARA_NAME[self.id][0] if self.id in _data.CHARA_NAME else _data.CHARA_NAME[UNKNOWN][0]

    @property
    def icon(self):
        dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'ark_avatar')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        c = OtherChara(self.id)
        return c.icon


    def render_icon(self, size, star_slot_verbose=True) -> Image:
        try:
            pic = self.icon.open().convert('RGBA').resize((size, size), Image.LANCZOS)
        except FileNotFoundError:
            logger.error(f'File not found: {self.icon.path}')

        l = size // 6
        star_lap = round(l * 0.15)
        margin_x = ( size - 6*l ) // 2
        margin_y = round(size * 0.05)
        if self.star:
            for i in range(5 if star_slot_verbose else min(self.star, 5)):
                a = i*(l-star_lap) + margin_x
                b = size - l - margin_y
                pic.paste(a, b, a+l, b+l)
        return pic


class OtherChara:
    def __init__(self, id):
        self.id = id

    @property
    def name(self):
        return _data.CHARA_NAME[self.id][0] if self.id in _data.CHARA_NAME else _data.CHARA_NAME[UNKNOWN][0]

    @property
    def icon(self):
        return R.img(f'{ICON_RES}/{ICON_PREFIX}{self.id + ID_OFFSET}.{ICON_EXT}')
