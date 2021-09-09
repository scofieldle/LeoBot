from typing import Dict, List
from .Utils import parseCondition

class Branch:
    def __init__(self, str):
        s = str.split(':')
        self.cond = parseCondition(s[0])
        self.id = int(s[1])
        self.evt:Event = None

class Event:
    def __init__(self, json):
        self.id: int = int(json['id'])
        self.name: str = json['event']
        self._include = parseCondition(json['include']) if 'include' in json else lambda _: True
        self._exclude = parseCondition(json['exclude']) if 'exclude' in json else lambda _: False
        self._effect: Dict[str, int] = json['effect'] if 'effect' in json else {}
        self.branch: List[Branch] = [Branch(x) for x in json['branch']] if 'branch' in json else []
        self._NoRandom = 'NoRandom' in json and json['NoRandom']
        self._postEvent = json['postEvent'] if 'postEvent' in json else None
    def __str__(self) -> str:
        return f'Event(id={self.id}, name={self.name})'
    def checkCondition(self, prop) -> bool:
        return not self._NoRandom and self._include(prop) and not self._exclude(prop)
    def runEvent(self, prop) -> List[str]:
        prop.apply(self._effect)
        for b in self.branch:
            if b.cond(prop):
                return [self.name] + b.evt.runEvent(prop)
        if self._postEvent: return [self.name, self._postEvent]
        return [self.name]