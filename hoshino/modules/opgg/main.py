#!/usr/bin/env python3
import sys, os, json, requests, time
from lxml import etree
import requests
from . import build
from . import skill_order
from . import tier_list
from . import runes
from hoshino import Service, aiorequests
from hoshino.typing import CQEvent, MessageSegment

_help = "输入 上/中/野/下/辅 查询各路排行\n输入 英雄名 查询技能加点、出装及天赋；英雄名后可跟位置以限定位置\n支持部分习惯昵称；若搜索失败，请使用官方称号\n例：opgg 愁云使者 中\n"
sv = Service('opgg', bundle='opgg', enable_on_default=True, help_=_help)

lanes = {
"top":"top","TOP":"top","上":"top","上路":"top",
"mid":"mid","MID":"mid","中":"mid","中路":"mid",
"jungle":"jungle","JUNGLE":"jungle","野":"jungle","打野":"jungle","野区":"jungle",
"adc":"adc","ADC":"adc","下":"adc","下路":"adc","ad":"adc",
"support":"support","SUPPORT":"support","辅":"support","辅助":"support",
"all":"all","ALL":"all"
}

officialName = {"暗黑元首":"Syndra","暗夜猎手":"Vayne","暗裔剑魔":"Aatrox","傲之追猎者":"Rengar","暴怒骑士":"Kled","暴走萝莉":"Jinx","爆破鬼才":"Ziggs","北地之怒":"Sejuani","冰晶凤凰":"Anivia","冰霜女巫":"Lissandra",
"不灭狂雷":"Volibear","不屈之枪":"Pantheon","不祥之刃":"Katarina","残月之肃":"Aphelios","潮汐海灵":"Fizz","惩戒之箭":"Varus","愁云使者":"Vex","翠神":"Ivern","大发明家":"Heimerdinger","刀锋舞者":"Irelia","刀锋之影":"Talon",
"德邦总管":"Xin Zhao","德玛西亚皇子":"Jarvan IV","德玛西亚之力":"Garen","德玛西亚之翼":"Quinn","涤魂圣枪":"Senna","堕落天使":"Morgana","恶魔小丑":"Shaco","发条魔灵":"Orianna","法外狂徒":"Graves","放逐之刃":"Riven",
"风暴之怒":"Janna","封魔剑魂":"Yone","弗雷尔卓德之心":"Braum","符文法师":"Ryze","复仇焰魂":"Brand","复仇之矛":"Kalista","光辉女郎":"Lux","诡术妖姬":"LeBlanc","海兽祭司":"Illaoi","海洋之灾":"Gangplank","含羞蓓蕾":"Lillia",
"寒冰射手":"Ashe","河流之王":"Tahm Kench","黑暗之女":"Annie","幻翎":"Rakan","唤潮鲛姬":"Nami","荒漠屠夫":"Renekton","魂锁典狱长":"Thresh","机械公敌":"Rumble","机械先驱":"Viktor","疾风剑豪":"Yasuo","皎月女神":"Diana",
"解脱者":"Sylas","荆棘之兴":"Zyra","九尾妖狐":"Ahri","酒桶":"Gragas","巨魔之王":"Trundle","卡牌大师":"Twisted Fate","狂暴之心":"Kennen","狂野女猎手":"Nidalee","狂战士":"Olaf","离群之刺":"Akali","炼金术士":"Singed",
"灵罗娃娃":"Gwen","龙血武姬":"Shyvana","麦林炮手":"Tristana","蛮族之王":"Tryndamere","盲僧":"Lee Sin","迷失之牙":"Gnar","魔法猫咪":"Yuumi","魔蛇之拥":"Cassiopeia","牧魂人":"Yorick","暮光星灵":"Zoe","暮光之眼":"Shen",
"逆羽":"Xayah","牛头酋长":"Alistar","扭曲树精":"Maokai","诺克萨斯统领":"Swain","诺克萨斯之手":"Darius","披甲龙龟":"Rammus","皮城女警":"Caitlyn","皮城执法官":"Vi","破败之王":"Viego","齐天大圣":"Wukong","琴瑟仙女":"Sona",
"青钢影":"Camille","荣耀行刑官":"Draven","熔岩巨兽":"Malphite","镕铁少女":"Rell","沙漠皇帝":"Azir","沙漠玫瑰":"Samira","沙漠死神":"Nasus","山隐之焰":"Ornn","殇之木乃伊":"Amumu","赏金猎人":"Miss Fortune","深海泰坦":"Nautilus",
"深渊巨口":"Kog'Maw","生化魔人":"Zac","圣锤之毅":"Poppy","圣枪游侠":"Lucian","时光守护者":"Zilean","时间刺客":"Ekko","兽灵行者":"Udyr","曙光女神":"Leona","水晶先锋":"Skarner","死亡颂唱者":"Karthus","探险家":"Ezreal",
"天启者":"Karma","铁铠冥魂":"Mordekaiser","痛苦之拥":"Evelynn","瓦洛兰之盾":"Taric","万花通灵":"Neeko","腕豪":"Sett","亡灵战神":"Sion","未来守护者":"Jayce","瘟疫之源":"Twitch","无极剑圣":"Master Yi","无双剑姬":"Fiora",
"无畏战车":"Urgot","武器大师":"Jax","戏命师":"Jhin","仙灵女巫":"Lulu","邪恶小法师":"Veigar","星界游神":"Bard","星籁歌姬":"Seraphine","猩红收割者":"Vladimir","虚空遁地兽":"Rek'Sai","虚空恐惧":"Cho'Gath","虚空掠夺者":"Kha'Zix",
"虚空先知":"Malzahar","虚空行者":"Kassadin","虚空之女":"Kai'Sa","虚空之眼":"Vel'Koz","雪原双子":"Nunu","血港鬼影":"Pyke","迅捷斥候":"Teemo","岩雀":"Taliyah","英勇投弹手":"Corki","影流之镰":"Kayn","影流之主":"Zed",
"影哨":"Akshan","永恒梦魇":"Nocturne","永猎双子":"Kindred","元素女皇":"Qiyana","远古恐惧":"Fiddlesticks","远古巫灵":"Xerath","战争女神":"Sivir","战争之影":"Hecarim","蒸汽机器人":"Blitzcrank","正义巨像":"Galio",
"正义天使":"Kayle","蜘蛛女皇":"Elise","众星之子":"Soraka","铸星龙王":"Aurelion Sol","祖安狂人":"Dr. Mundo","祖安怒兽":"Warwick"}

championLane = {
"top": {"Camille","Vayne","Graves","Fiora","Shen","Teemo","Irelia","Darius","Tahm Kench","Jax","Jayce","Poppy","Tryndamere","Malphite","Viktor","Aatrox","Sett","Renekton","Zac","Quinn","Rengar","Garen","Ornn","Yasuo","Yorick","Kennen","Sylas","Kayle","Yone","Cassiopeia","Akali","Vladimir","Sion","Nasus","Heimerdinger","Gangplank","Kled","Dr. Mundo","Gwen","Wukong","Singed","Lillia","Rumble","Trundle","Mordekaiser","Cho'Gath","Gnar","Urgot","Maokai","Riven","Lucian","Volibear","Gragas","Ryze","Warwick","Kassadin","Sejuani","Illaoi","Karma"},
"jungle":{"Lee Sin","Graves","Xin Zhao","Rek'Sai","Viego","Elise","Shaco","Poppy","Nidalee","Warwick","Zac","Talon","Ekko","Hecarim","Master Yi","Kindred","Kayn","Kha'Zix","Vi","Fiddlesticks","Jarvan IV","Taliyah","Nunu & Willump","Nocturne","Karthus","Gragas","Rammus","Zed","Trundle","Shyvana","Udyr","Lillia","Evelynn","Gwen","Skarner","Olaf","Ivern","Amumu","Diana","Rengar","Qiyana","Sejuani","Rumble","Volibear"},
"mid":{"Vex","Zed","Katarina","Sett","LeBlanc","Singed","Twisted Fate","Kassadin","Talon","Anivia","Yasuo","Yone","Malphite","Sylas","Akshan","Akali","Ekko","Viktor","Tryndamere","Qiyana","Galio","Annie","Cassiopeia","Lissandra","Pantheon","Xerath","Zoe","Ahri","Lux","Orianna","Irelia","Fizz","Malzahar","Syndra","Diana","Vladimir","Aurelion Sol","Renekton","Lucian","Ryze","Veigar","Azir","Nunu & Willump","Rumble","Garen","Neeko","Corki"},
"adc":{"Vayne","Jhin","Caitlyn","Jinx","Ezreal","Lucian","Ziggs","Draven","Miss Fortune","Samira","Xayah","Ashe","Aphelios","Kai'Sa","Kog'Maw","Swain","Twitch","Yasuo","Sivir","Kalista","Tristana","Varus","Cassiopeia"},
"support":{"Blitzcrank","Leona","Xerath","Lulu","Thresh","Nami","Morgana","Lux","Rell","Maokai","Shaco","Nautilus","Yuumi","Karma","Alistar","Rakan","Pyke","Zilean","Senna","Brand","Anivia","Amumu","Soraka","Zyra","Sona","Pantheon","Heimerdinger","Gragas","Braum","Vel'Koz","Veigar","Taliyah","Swain","Neeko","Poppy","Vex","Janna","Twitch","Bard","Galio","Fiddlesticks","Zac","Sett","Miss Fortune","Taric","Seraphine","Shen","Trundle"}
}

nicknames = {
    '暗裔剑魔': 'Aatrox','剑魔': 'Aatrox','暗裔病魔': 'Aatrox','亚托克斯': 'Aatrox','天神下凡': 'Aatrox','Aatrox': 'Aatrox',
    '九尾妖狐': 'Ahri','阿狸': 'Ahri','狐狸': 'Ahri','Ahri': 'Ahri',
    '暗影之拳': 'Akali','阿卡丽': 'Akali','AKL': 'Akali','Akali': 'Akali',
    '牛头酋长': 'Alistar','牛头': 'Alistar','阿利斯塔': 'Alistar','Alistar': 'Alistar',
    '殇之木乃伊': 'Amumu','阿木木': 'Amumu','木木': 'Amumu','Amumu': 'Amumu',
    '冰晶凤凰': 'Anivia','艾尼维亚': 'Anivia','冰鸟': 'Anivia','Anivia': 'Anivia',
    '黑暗之女': 'Annie','火焰波比': 'Annie','安妮': 'Annie','Annie': 'Annie',
    '寒冰射手': 'Ashe','艾希': 'Ashe','Ashe': 'Ashe',
    '铸星龙王': 'Aurelion Sol','龙王': 'Aurelion Sol','奥瑞利安.索尔': 'Aurelion Sol','Aurelion Sol': 'Aurelion Sol',
    '沙漠皇帝': 'Azir','沙皇': 'Azir','阿兹尔': 'Azir','Azir': 'Azir',
    '星界游神': 'Bard','巴德': 'Bard','Bard': 'Bard',
    '蒸汽机器人': 'Blitzcrank','机器人': 'Blitzcrank','布里茨': 'Blitzcrank','Blitzcrank': 'Blitzcrank',
    '复仇焰魂': 'Brand','布兰德': 'Brand','火男': 'Brand','Brand': 'Brand',
    '弗雷尔卓德之心': 'Braum','布隆': 'Braum','Braum': 'Braum',
    '皮城女警': 'Caitlyn','女警': 'Caitlyn','凯特琳': 'Caitlyn','小蛋糕': 'Caitlyn','Caitlyn': 'Caitlyn',
    '青钢影': 'Camille','卡密尔': 'Camille','卡蜜儿': 'Camille','Camille': 'Camille',
    '魔蛇之拥': 'Cassiopeia','卡西奥佩娅': 'Cassiopeia','蛇女': 'Cassiopeia','Cassiopeia': 'Cassiopeia',
    '虚空恐惧': "Cho'Gath",'科加斯': "Cho'Gath",'大虫子': "Cho'Gath","Cho'Gath": "Cho'Gath",
    '英勇投弹手': 'Corki','库奇': 'Corki','飞机': 'Corki','Corki': 'Corki',
    '洛克萨斯之手': 'Darius','德莱厄斯': 'Darius','诺手': 'Darius','诺克': 'Garen','Darius': 'Darius',
    '皎月女神': 'Diana','皎月': 'Diana','戴安娜': 'Diana','Diana': 'Diana',
    '荣耀行刑官': 'Draven','德莱文': 'Draven','Draven': 'Draven',
    '祖安狂人': 'Dr. Mundo','蒙多': 'Dr. Mundo','Dr. Mundo': 'Dr. Mundo',
    '时间刺客': 'Ekko','艾克': 'Ekko','Ekko': 'Ekko',
    '蜘蛛女皇': 'Elise','蜘蛛': 'Elise','伊莉丝': 'Elise','Elise': 'Elise',
    '痛苦之拥': 'Evelynn','伊芙琳': 'Evelynn','寡妇': 'Evelynn','Evelynn': 'Evelynn',
    '探险家': 'Ezreal','伊泽瑞尔': 'Ezreal','EZ': 'Ezreal','Ezreal': 'Ezreal',
    '末日使者': 'Fiddlesticks','费德提克': 'Fiddlesticks','稻草人': 'Fiddlesticks','Fiddlesticks': 'Fiddlesticks',
    '无双剑姬': 'Fiora','剑姬': 'Fiora','菲欧娜': 'Fiora','Fiora': 'Fiora',
    '潮汐海灵': 'Fizz','菲兹': 'Fizz','小鱼人': 'Fizz','Fizz': 'Fizz',
    '正义巨像': 'Galio','加里奥': 'Galio','Galio': 'Galio',
    '海洋之灾': 'Gangplank','普朗克': 'Gangplank','船长': 'Gangplank','Gangplank': 'Gangplank',
    '德玛西亚之力': 'Garen','盖伦': 'Garen','大宝剑': 'Garen','德玛': 'Garen','Garen': 'Garen',
    '迷失之牙': 'Gnar','纳尔': 'Gnar','Gnar': 'Gnar',
    '酒桶': 'Gragas','啤酒人': 'Gragas','古拉加斯': 'Gragas','Gragas': 'Gragas',
    '法外狂徒': 'Graves','格雷福斯': 'Graves','男枪': 'Graves','Graves': 'Graves',
    '战争之影': 'Hecarim','赫卡里姆': 'Hecarim','人马': 'Hecarim','Hecarim': 'Hecarim',
    '大发明家': 'Heimerdinger','黑默丁格': 'Heimerdinger','大头': 'Heimerdinger','Heimerdinger': 'Heimerdinger',
    '海兽祭司': 'Illaoi','俄洛伊': 'Illaoi','触手妈': 'Illaoi','Illaoi': 'Illaoi',
    '刀锋舞者': 'Irelia','刀妹': 'Irelia','艾瑞莉娅': 'Irelia','Irelia': 'Irelia',
    '翠神': 'Ivern','蔡徐坤': 'Ivern','艾翁': 'Ivern','Ivern': 'Ivern',
    '风暴之怒': 'Janna','风女': 'Janna','迦娜': 'Janna','Janna': 'Janna',
    '德玛西亚皇子': 'Jarvan IV','皇子': 'Jarvan IV','嘉文四世': 'Jarvan IV','Jarvan IV': 'Jarvan IV',
    '武器大师': 'Jax','武器': 'Jax','贾克斯': 'Jax','Jax': 'Jax',
    '未来守护者': 'Jayce','杰斯': 'Jayce','Jayce': 'Jayce',
    '戏命师': 'Jhin','烬': 'Jhin','Jhin': 'Jhin',
    '暴走萝莉': 'Jinx','金克丝': 'Jinx','爆爆': 'Jinx','Jinx': 'Jinx',
    '虚空之女': "Kai'Sa",'卡莎': "Kai'Sa","Kai'Sa": "Kai'Sa",
    '复仇之矛': 'Kalista','滑板鞋': 'Kalista','卡莉丝塔': 'Kalista','Kalista': 'Kalista',
    '天启者': 'Karma','卡尔玛': 'Karma','扇子妈': 'Karma','Karma': 'Karma',
    '死亡歌颂者': 'Karthus','死歌': 'Karthus','卡尔萨斯': 'Karthus','Karthus': 'Karthus',
    '虚空行者': 'Kassadin','卡萨丁': 'Kassadin','Kassadin': 'Kassadin',
    '不祥之刃': 'Katarina','卡特': 'Katarina','卡特琳娜': 'Katarina','Katarina': 'Katarina',
    '审判天使': 'Kayle','天使': 'Kayle','凯尔': 'Kayle','Kayle': 'Kayle',
    '影流之镰': 'Kayn','凯隐': 'Kayn','Kayn': 'Kayn',
    '狂暴之心': 'Kennen','凯南': 'Kennen','电耗子': 'Kennen','Kennen': 'Kennen',
    '虚空掠夺者': "Kha'Zix",'卡兹克': "Kha'Zix",'螳螂': "Kha'Zix","Kha'Zix": "Kha'Zix",
    '永猎双子': 'Kindred','千珏': 'Kindred','Kindred': 'Kindred',
    '暴怒骑士': 'Kled','克烈': 'Kled','Kled': 'Kled',
    '深渊巨口': "Kog'Maw",'克格莫': "Kog'Maw",'大嘴': "Kog'Maw","Kog'Maw": "Kog'Maw",
    '诡术妖姬': 'LeBlanc','妖姬': 'LeBlanc','乐芙兰': 'LeBlanc','LeBlanc': 'LeBlanc',
    '盲僧': 'Lee Sin','李青': 'Lee Sin','瞎子': 'Lee Sin','Lee Sin': 'Lee Sin',
    '曙光女神': 'Leona','蕾欧娜': 'Leona','女坦': 'Leona','日女': 'Leona','Leona': 'Leona',
    '冰霜女巫': 'Lissandra','丽桑卓': 'Lissandra','冰女': 'Lissandra','Lissandra': 'Lissandra',
    '圣枪游侠': 'Lucian','卢锡安': 'Lucian','奥巴马': 'Lucian','Lucian': 'Lucian',
    '仙灵女巫': 'Lulu','璐璐': 'Lulu','露露': 'Lulu','Lulu': 'Lulu',
    '光辉女郎': 'Lux','光辉': 'Lux','拉克丝': 'Lux','Lux': 'Lux',
    '熔岩巨兽': 'Malphite','墨菲特': 'Malphite','石头人': 'Malphite','石头': 'Malphite','Malphite': 'Malphite',
    '虚空先知': 'Malzahar','马尔扎哈': 'Malzahar','蚂蚱': 'Malzahar','Malzahar': 'Malzahar',
    '扭曲树精': 'Maokai','茂凯': 'Maokai','大树': 'Maokai','Maokai': 'Maokai',
    '无极剑圣': 'Master Yi','剑圣': 'Master Yi','易': 'Master Yi','易大师': 'Master Yi','Master Yi': 'Master Yi',
    '赏金猎人': 'Miss Fortune','厄运小姐': 'Miss Fortune','女枪': 'Miss Fortune','Miss Fortune': 'Miss Fortune',
    '齐天大圣': 'Wukong','孙悟空': 'Wukong','猴子': 'Wukong','Wukong': 'Wukong',
    '铁铠冥魂': 'Mordekaiser','莫德凯撒': 'Mordekaiser','铁男': 'Mordekaiser','Mordekaiser': 'Mordekaiser',
    '堕落天使': 'Morgana','莫甘娜': 'Morgana','Morgana': 'Morgana',
    '唤潮鲛姬': 'Nami','娜美': 'Nami','Nami': 'Nami',
    '沙漠死神': 'Nasus','内瑟斯': 'Nasus','狗头': 'Nasus','Nasus': 'Nasus',
    '深海泰坦': 'Nautilus','泰坦': 'Nautilus','诺提勒斯': 'Nautilus','Nautilus': 'Nautilus',
    '狂野女猎手': 'Nidalee','奈德丽': 'Nidalee','豹女': 'Nidalee','Nidalee': 'Nidalee',
    '永恒梦魇': 'Nocturne','梦魇': 'Nocturne','魔腾': 'Nocturne','Nocturne': 'Nocturne',
    '雪人骑士': 'Nunu','努努': 'Nunu','Nunu': 'Nunu',
    '狂战士': 'Olaf','奥拉夫': 'Olaf','Olaf': 'Olaf',
    '发条魔灵': 'Orianna','发条': 'Orianna','奥利安娜': 'Orianna','Orianna': 'Orianna',
    '山隐之焰': 'Ornn','奥恩': 'Ornn','Ornn': 'Ornn',
    '战争之王': 'Pantheon','不屈之枪': 'Pantheon','潘森': 'Pantheon','Pantheon': 'Pantheon',
    '圣锤之毅': 'Poppy','波比': 'Poppy','Poppy': 'Poppy',
    '血港鬼影': 'Pyke','派克': 'Pyke','Pyke': 'Pyke',
    '德玛西亚之翼': 'Quinn','奎因': 'Quinn','鸟人': 'Quinn','Quinn': 'Quinn',
    '幻翎': 'Rakan','洛': 'Rakan','Rakan': 'Rakan',
    '披甲龙龟': 'Rammus','龙龟': 'Rammus','拉莫斯': 'Rammus','Rammus': 'Rammus',
    '虚空遁地兽': "Rek'Sai",'雷克赛': "Rek'Sai",'挖掘机': "Rek'Sai","Rek'Sai": "Rek'Sai",
    '荒漠屠夫': 'Renekton','雷克顿': 'Renekton','鳄鱼': 'Renekton','Renekton': 'Renekton',
    '傲之追猎者': 'Rengar','雷恩加尔': 'Rengar','狮子狗': 'Rengar','Rengar': 'Rengar',
    '放逐之刃': 'Riven','锐雯': 'Riven','Riven': 'Riven',
    '机械公敌': 'Rumble','兰博': 'Rumble','Rumble': 'Rumble',
    '符文法师': 'Ryze','瑞兹': 'Ryze','Ryze': 'Ryze',
    '北地之怒': 'Sejuani','瑟庄妮': 'Sejuani','猪妹': 'Sejuani','Sejuani': 'Sejuani',
    '恶魔小丑': 'Shaco','小丑': 'Shaco','萨科': 'Shaco','Shaco': 'Shaco',
    '暮光之眼': 'Shen','慎': 'Shen','Shen': 'Shen',
    '龙血武姬': 'Shyvana','希瓦娜': 'Shyvana','龙女': 'Shyvana','Shyvana': 'Shyvana',
    '炼金术士': 'Singed','炼金': 'Singed','辛吉德': 'Singed','Singed': 'Singed',
    '亡灵战神': 'Sion','赛恩': 'Sion','老司机': 'Sion','Sion': 'Sion',
    '战争女神': 'Sivir','希维尔': 'Sivir','轮子妈': 'Sivir','Sivir': 'Sivir',
    '水晶先锋': 'Skarner','斯卡纳': 'Skarner','蝎子': 'Skarner','Skarner': 'Skarner',
    '琴瑟仙女': 'Sona','娑娜': 'Sona','琴女': 'Sona','Sona': 'Sona',
    '众星之子': 'Soraka','索拉卡': 'Soraka','奶妈': 'Soraka','Soraka': 'Soraka',
    '诺克萨斯统领': 'Swain','斯维因': 'Swain','乌鸦': 'Swain','Swain': 'Swain',
    '暗黑元首': 'Syndra','辛德拉': 'Syndra','Syndra': 'Syndra',
    '河流之王': 'Tahm Kench','塔姆': 'Tahm Kench','Tahm Kench': 'Tahm Kench',
    '岩雀': 'Taliyah','塔莉亚': 'Taliyah','Taliyah': 'Taliyah',
    '刀锋之影': 'Talon','泰隆': 'Talon','男刀': 'Talon','Talon': 'Talon',
    '瓦诺兰之盾': 'Taric','塔里克': 'Taric','宝石': 'Taric','Taric': 'Taric',
    '迅捷斥候': 'Teemo','提莫': 'Teemo','Teemo': 'Teemo',
    '魂锁典狱长': 'Thresh','锤石': 'Thresh','Thresh': 'Thresh',
    '麦林炮手': 'Tristana','崔斯塔娜': 'Tristana','小炮': 'Tristana','Tristana': 'Tristana',
    '巨魔之王': 'Trundle','巨魔': 'Trundle','特朗德尔': 'Trundle','Trundle': 'Trundle',
    '蛮族之王': 'Tryndamere','蛮王': 'Tryndamere','泰达米尔': 'Tryndamere','Tryndamere': 'Tryndamere',
    '卡牌大师': 'Twisted Fate','卡牌': 'Twisted Fate','崔斯特': 'Twisted Fate','Twisted Fate': 'Twisted Fate',
    '瘟疫之源': 'Twitch','图奇': 'Twitch','老鼠': 'Twitch','Twitch': 'Twitch',
    '兽灵行者': 'Udyr','乌迪尔': 'Udyr','Udyr': 'Udyr',
    '无畏战车': 'Urgot','厄加特': 'Urgot','螃蟹': 'Urgot','Urgot': 'Urgot',
    '惩戒之箭': 'Varus','韦鲁斯': 'Varus','Varus': 'Varus',
    '暗夜猎手': 'Vayne','薇恩': 'Vayne','VN': 'Vayne','Vayne': 'Vayne',
    '邪恶小法师': 'Veigar','小法': 'Veigar','维迦': 'Veigar','Veigar': 'Veigar',
    '虚空之眼': "Vel'Koz",'维克兹': "Vel'Koz",'大眼': "Vel'Koz","Vel'Koz": "Vel'Koz",
    '皮城执法官': 'Vi','蔚': 'Vi','WEI': 'Vi','Vi': 'Vi',
    '机械先驱': 'Viktor','维克托': 'Viktor','三只手': 'Viktor','Viktor': 'Viktor',
    '猩红收割者': 'Vladimir','弗拉基米尔': 'Vladimir','吸血鬼': 'Vladimir','Vladimir': 'Vladimir',
    '雷霆咆哮': 'Volibear','沃利贝尔': 'Volibear','狗熊': 'Volibear','Volibear': 'Volibear',
    '祖安怒兽': 'Warwick','沃里克': 'Warwick','狼人': 'Warwick','Warwick': 'Warwick',
    '逆羽': 'Xayah','霞': 'Xayah','Xayah': 'Xayah',
    '远古巫灵': 'Xerath','泽拉斯': 'Xerath','Xerath': 'Xerath',
    '德邦总管': 'Xin Zhao','赵信': 'Xin Zhao','Xin Zhao': 'Xin Zhao',
    '疾风剑豪': 'Yasuo','亚索': 'Yasuo','Yasuo': 'Yasuo',
    '牧魂人': 'Yorick','约里克': 'Yorick','掘墓': 'Yorick','Yorick': 'Yorick',
    '生化魔人': 'Zac','扎克': 'Zac','Zac': 'Zac',
    '影流之主': 'Zed','劫': 'Zed','Zed': 'Zed',
    '爆破鬼才': 'Ziggs','吉格斯': 'Ziggs','炸弹人': 'Ziggs','Ziggs': 'Ziggs',
    '时光守护者': 'Zilean','时光': 'Zilean','基兰': 'Zilean','老头': 'Zilean','Zilean': 'Zilean',
    '暮光星灵': 'Zoe','佐伊': 'Zoe','Zoe': 'Zoe',
    '荆棘之兴': 'Zyra','婕拉': 'Zyra','Zyra': 'Zyra',
    '熬夜波比':'Vex','薇古丝':'Vex',
    '阿克尚':'Akshan',
    '塞拉斯':'Sylas','偷男':'Sylas',
    '永恩':'Yone',
    '琪亚娜':'Qiyana','kiana':'Qiyana',
    '瑟提':'Sett','劲夫':'Sett',
    '妮蔻':'Neeko','变色龙':'Neeko',
    '芮尔':'Rell',
    '悠米':'Yuumi','猫咪':'Yuumi',
    '塞纳':'Senna',
    '萨勒芬妮':'Seraphine','歌姬':'Seraphine',
    '萨米拉':'Samira',
    '厄斐琉斯':'Aphelios','efls':'Aphelios',
    '破败王':'Viego','佛耶戈':'Viego',
    '莉莉娅':'Lillia',
    '格温':'Gwen','剪刀妹':'Gwen'
}

ip_list = []

def load_config():
    global ip_list
    ip_list = []
    with open(os.path.join(os.path.dirname(__file__), 'ip_list.txt'), 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            if line:
                ip_list.append(line.replace('\n',''))
            line = f.readline()

def save_config():
    global ip_list
    if ip_list:
        with open(os.path.join(os.path.dirname(__file__), 'ip_list.txt'), 'w', encoding='utf-8') as f:
            for ip in ip_list:
                if ip:
                    f.write(ip.replace('\n',''))
                    f.write('\n')

load_config()

# 设置代理服务器
async def get_ip_list(url):
    global ip_list
    html = await aiorequests.get(url, headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"})
    tree = etree.HTML(await html.text)
    ips = tree.xpath('//table[@class="table table-hover table-bordered"]/tbody/tr')
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.xpath('td')
        del_time = tds[7].xpath("string(.)")
        if tds[4].xpath("string(.)") == '支持' and tds[5].xpath("string(.)") == '支持' and (del_time.startswith('0.') or del_time.startswith('1.') or del_time.startswith('2.') or del_time.startswith('3.')):
            ip = 'https://'+tds[0].xpath("string(.)") + ':' + tds[1].xpath("string(.)")
            if ip and not ip in ip_list:
                ip_list.append(ip)

def help_message():
    print(_help)


import copy
msgs = []
dic = {}
dat = {}
def resetMsg(ev):
    msgs.clear()
    dic["type"] = "node"
    dic["data"] = dat
    dat["name"] = "ebq"
    dat["uin"] = str(ev.self_id)

def packing(st):
    dat["content"] = st
    msgs.append(copy.deepcopy(dic))

async def getInfo(x, y, bot, ev):
    #resetMsg(ev)
    y = y.replace(" ", '')
    
    skills = skill_order.get(x, y)
    #packing("加点：\n" + skill_order.display(skills))
    await bot.send(ev, "加点：\n" + skill_order.display(skills))
    
    build_list = build.get(x, y, ip_list[0])
    if not build_list:
        print('代理访问失败了')
        del ip_list[0]
        save_config()
        load_config()
        build_list = build.get(x, y, '')
    #packing("出装：\n" + build.display(build_list))
    await bot.send(ev, "出装：\n" + build.display(build_list))
    
    
    rune_guide = runes.get(x, y, ip_list[0])
    if not rune_guide:
        print('代理访问失败了')
        del ip_list[0]
        save_config()
        load_config()
        rune_guide = runes.get(x, y, '')
    #packing("天赋：\n" + runes.display(rune_guide))
    await bot.send(ev, "天赋：" + runes.display(rune_guide))

    #await bot.send_group_forward_msg(group_id = ev.group_id, messages = msgs)
    
    

@sv.on_prefix('opgg')
async def main(bot, ev:CQEvent):
    try:
        info = ev.message.extract_plain_text().strip()
        print(info)
        if info in ["", "help", "帮助"]:
            await bot.finish(ev, _help)
        if ' ' in info:
            info = [' '.join(info.split(' ')[:-1]), info.split(' ')[-1]]
        else:
            info = [info] 
        print(info)
        if info[0] in lanes:
            lane = lanes[info[0]]
            if lane == "all" or lane == "ALL":
                resetMsg(ev)
                for indv in championLane:
                    place, name, win_rate, ban_rate = tier_list.get(indv)
                    packing(tier_list.display(place, name, win_rate, ban_rate, indv))
                await bot.send_group_forward_msg(group_id = ev.group_id, messages = msgs) # 合并转发就没发出来过，就没写在help里了
            else:
                place, name, win_rate, ban_rate = tier_list.get(lane)
                await bot.send(ev, tier_list.display(place, name, win_rate, ban_rate, lane))
        else:
            if info[0] in nicknames:
                info[0] = nicknames[info[0]]
            elif info[0] in officialName:
                info[0] = officialName[info[0]]
            elif info[0] in officialName.values():
                pass
            else:
                help_message()
                await bot.finish(ev, "未找到该英雄\n支持部分习惯昵称；若搜索失败，请使用官方称号\n例：opgg愁云使者 中\n")
            print(info[0])
            if len(info) > 1 and info[1] in lanes and info[0] in championLane[lanes[info[1]]]:
                info[1] = lanes[info[1]]
                print(info[1])
                await getInfo(info[1], info[0], bot, ev)
            else:
                pos = []
                for indv in championLane:
                    if info[0] in championLane[indv]:
                        pos.append(indv)
                if len(pos) == 1:
                    await getInfo(pos[0], info[0], bot, ev)
                else:
                    await bot.send(ev, "该英雄出现在多路：" + ' '.join(pos) + "\n请指定一个位置\n例：opgg " + info[0] + ' ' + pos[0])

    except requests.exceptions.ConnectionError:
        print("\nCONNECTION ERROR - check connection and try again")
        
@sv.on_fullmatch('更新lol代理池')
async def up_ip_list(bot, ev):
    await bot.send(ev, '开始更新')
    for i in range(20):
        url = f'https://ip.ihuan.me/address/5Lit5Zu9.html?page={i}'
        await get_ip_list(url)
        time.sleep(0.5)
    save_config()
    load_config()
    await bot.send(ev, f'更新完成，目前代理池IP数量为{len(ip_list)}')

@sv.scheduled_job('interval', minutes=5)
async def schedule_ip_list():
    if len(ip_list) < 20:
        for i in range(20):
            url = f'https://ip.ihuan.me/address/5Lit5Zu9.html?Page={i}'
            await get_ip_list(url)
            time.sleep(0.5)
        save_config()
        load_config()
    return
