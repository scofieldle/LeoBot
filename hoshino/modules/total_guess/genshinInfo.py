#-*- coding: utf-8 -*-
import re, xlwt, time
from lxml import etree
import requests, json
from selenium import webdriver

chara = []
with open(r'D:\eclipse-workspace\bilibili\Genshin_Impact\char_name.json','r',encoding='utf-8') as f:
    json_data = json.load(f)
    for key in json_data.keys():
        chara.append(key)

total = {}
    
def get_1(name, tree):
    global total
    colspan_1 = tree.xpath('//td[@colspan="1"]')
    detail = tree.xpath('//div[@class="skill_desc_layout"]')
    for i in range(6):
        total[name]['技能'].append([colspan_1[i].xpath("string(.)"),detail[i].xpath("string(.)")])
    for i in range(6,12):
        total[name]['命之座'].append([colspan_1[i].xpath("string(.)"),detail[i].xpath("string(.)")])
    
def get_2(name, tree):
    global total
    colspan_2 = tree.xpath('//td[@colspan="2"]')
    for i in range(0,16,2):
        total[name]['故事'].append([colspan_2[-(i+2)].xpath("string(.)"),colspan_2[-(i+1)].xpath("string(.)")])
        
def get_5(name, tree):
    global total
    colspan_5 = tree.xpath('//td[@colspan="5"]')
    for i in range(len(colspan_5)-1,0,-2):
        if colspan_5[i].xpath("string(.)").isalpha():
            break
        total[name]['语音'].append([colspan_5[i-1].xpath("string(.)"),colspan_5[i].xpath("string(.)")])


def start():
    global total
    for name in chara:
        url = f'https://genshin.honeyhunterworld.com/db/char/{name}/?lang=CHS'
        html = requests.get(url)
        tree = etree.HTML(html.text)
        time.sleep(1)

        total[name] = {'技能':[],'故事':[],'命之座':[],'语音':[]}
        get_1(name, tree)
        get_2(name, tree)
        get_5(name, tree)
        print(name)

start()

with open(r'D:\eclipse-workspace\bilibili\Genshin_Impact\Genshin_chara.json', 'w', encoding='utf-8') as f:
    json.dump(total,f,indent=4,ensure_ascii=False)
print('successfully ouput')