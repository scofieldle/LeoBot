# -*- coding:utf-8 -*-

import os

def getQqName(uid):
    p = os.path.dirname(__file__) + f'/qqdata/{str(uid)}.ini'
    mark = "熊猫头"
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as f:
            mark = f.read()
            mark = mark.strip()
    return mark

def setQqName(uid,msg):
    msg = str(msg)
    p = os.path.dirname(__file__) + f'/qqdata/{str(uid)}.ini'
    with open(p,"w",encoding="utf-8") as f:
        f.write(msg)
        return msg