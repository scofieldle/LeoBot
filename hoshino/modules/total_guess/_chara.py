import importlib
import pygtrie
from hoshino import R, util, log
from . import mrfz_data

UNKNOWN = 1000

logger = log.new_logger('other_chara')


class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()

    def update(self):
        importlib.reload(mrfz_data)
        self._roster.clear()
        for idx, names in mrfz_data.CHARA_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'OtherChara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        self._all_name_list = self._roster.keys()

    def get_id(self, name):
        name = util.normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN


roster = Roster()


def name2id(name):
    return roster.get_id(name)


class OtherChara:
    def __init__(self, id):
        self.id = id

    @property
    def name(self):
        return mrfz_data.CHARA_NAME[self.id][0] if self.id in mrfz_data.CHARA_NAME else mrfz_data.CHARA_NAME[UNKNOWN][0]

    @property
    def icon(self):
        return R.img(f'ark_avatar/Operator{self.id - 1000}.jpg')
