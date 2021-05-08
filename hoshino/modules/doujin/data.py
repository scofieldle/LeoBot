from .nhentai import *
import ujson as json

def get_random_doujin_list(num):
    a = []
    for n in range(num):
        print(n)
        d = get_random_id()
        b = get_doujin(d)
        a.append(b.__dict__)
    return a


def get_search_doujin_list(query, num):
    b = search(query, 1, "date")
    b = b[:num]
    a = []
    for each in b:
        a.append(each.__dict__)
    return a


def get_msg_by_doujin(doujin):
    msg_list = []
    msg = f'''神秘六位数:{doujin['id']}
名字（翻译后）:{doujin['titles']['english']}
名字（原文）:{doujin['titles']['japanese']}
收藏数量:{doujin['favorites']}
'''
    print(msg)
    msg = f'[CQ:message,text={msg}]'
    msg_list.append(msg)
    msg_list.append(f'[CQ:image,file={doujin["thumbnail"]}]')
    for each in doujin['pages']:
        msg_list.append(f'[CQ:image,file={each[0]}]')
    return msg_list
