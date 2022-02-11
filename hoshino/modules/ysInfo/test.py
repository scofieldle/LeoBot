import random, os, json, re, time, datetime
import urllib, requests
import string
import hashlib
import math
from io import BytesIO
from  PIL import Image,ImageFont,ImageDraw
import io
import base64
from threading import Lock
from urllib.parse import urlencode
from lxml import etree

mhyVersion = "2.11.1"
client_type = "5"

FILE_PATH = os.path.dirname(__file__)
COOKIE_PATH = os.path.join(FILE_PATH,'cookie.json')
user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25", 
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1"
]
cache_Cookie = {}
cookie = "cookie_token=aKMGRh4XPN4MPkTQgz5zdChwJXKU17YBCZlBEW4X;account_id=261898872;ltuid=261898872;ltoken=1E50eSuGaR8Lb8nU2uXU2H3VV1nfHljIrXgGCqOs"

def load_cookie():
    global cache_Cookie
    with open(COOKIE_PATH, 'r', encoding='utf-8') as f:
        cache_Cookie = json.load(f)

load_cookie()

def save_cookie():
    global cache_Cookie
    with open(COOKIE_PATH, 'w', encoding='utf8') as f:
        json.dump(cache_Cookie, f, ensure_ascii=False, indent=4)

def get_cookie():
    global cache_Cookie
    key = random.choice(list(cache_Cookie["cookie"].keys()))
    return cache_Cookie["cookie"][key]

def __md5__(text):
    _md5 = hashlib.md5()
    _md5.update(text.encode())
    return _md5.hexdigest()

def __get_ds__(query, body=None):
    if body:
        body = json.dumps(body)
    n = "xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs" # Github-@lulu666lulu
    i = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    q = '&'.join([f'{k}={v}' for k, v in query.items()])
    c = __md5__("salt=" + n + "&t=" + i + "&r=" + r + '&b=' + (body or '') + '&q=' + q)
    return i + "," + r + "," + c

def request_data(uid=0, api='index', character_ids=None):
    server = 'cn_gf01'
    if uid[0] == "5":
        server = 'cn_qd01'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        "User-Agent": random.choice(user_agent),
        "Referer": "https://webstatic.mihoyo.com/",
        "x-rpc-app_version": "2.11.1",
        "x-rpc-client_type": '5',
        "DS": "",
        'Cookie': get_cookie()
    }

    params = {"role_id": uid, "server": server}

    json_data = None
    fn = requests.get
    base_url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/%s'
    url = base_url % api + '?'
    if api == 'index':
        url += urlencode(params)
    elif api == 'character':
        fn = requests.post
        json_data = {"character_ids": character_ids,"role_id": uid, "server": server}
        params = {}

    headers['DS'] = __get_ds__(params, json_data)
    req = ''
    if api == 'index':
        req = fn(url=url, headers=headers, json=json_data, timeout=10)
    else:
        try:
            req = fn(url=url, headers=headers, json=json_data, timeout=10)
        except:
            req = ''
    if req:
        return json.loads(req.text)
    return

def calcStringLength(text):
    # 令len(str(string).encode()) = m, len(str(string)) = n
    # 字符串所占位置长度 = (m + n) / 2
    # 但由于'·'属于一个符号而非中文字符所以需要把长度 - 1
    if re.search('·', text) is not None:
        stringlength = int(((str(text).encode()) + len(str(text)) - 1) / 2)
    elif re.search(r'[“”]', text) is not None:
        stringlength = int((len(str(text).encode()) + len(str(text))) / 2) - 2
    else:
        stringlength = int((len(str(text).encode()) + len(text)) / 2)

    return stringlength

def spaceWrap(text, flex=10):
    stringlength = calcStringLength(text)

    return '%s' % (str(text)) + '%s' % (' ' * int((int(flex) - stringlength)))

def elementDict(text, isOculus=False):
    elementProperty = str(re.sub(r'culus_number$', '', text)).lower()
    elementMastery = {
        "anemo": "风",
        "pyro": "火",
        "geo": "岩",
        "electro": "雷",
        "cryo": "冰",
        "hydro": "水",
        "dendro": "草",  # https://genshin-impact.fandom.com/wiki/Dendro
        "none": "无",
    }
    if elementProperty in elementMastery.keys():
        elementProperty = str(elementMastery[elementProperty])
    else:
        elementProperty = "草"
    if isOculus:
        return elementProperty + "神瞳"
    elif not isOculus:
        return elementProperty + "属性"

def load_character():
    temp = {}
    with open(os.path.join(FILE_PATH,'character.json'), 'r', encoding='utf-8') as f:
        temp = json.load(f)
    return temp.keys()

def request_all_avatar(uid, raw_data):
    try:
        avatar_number = raw_data['data']['stats']['avatar_number']
    except:
        return ''
    print('uid: %s 获取全部角色信息' % uid)
    all_character = list(load_character())

    temp = request_data(uid=uid, api='character', character_ids=[10000003])
    if temp['data']:
        print(temp['data'])
        raw_data['data']['avatars'].append(temp['data']['avatars'][0])
        return raw_data

    return raw_data

def JsonAnalysis(info, Uid):
    if info:
        if info["retcode"] == 10001:
            return "Cookie错误/过期，请重置Cookie"
        if info["retcode"] != 0:
            return ("Api报错，返回内容为："+ info)
    else:
        return "UID输入错误 or 不存在"
    data = info
    time.sleep(1)
    dataC = request_all_avatar(Uid, info)
    if not dataC:
        return '无法查询到此UID'
    Character_datas = dataC["data"]["avatars"]
    return Character_datas
    
    
def genshin(uid):
    info = request_data(uid=uid)
    if info:
        mes = JsonAnalysis(info, uid)
    return mes

cache = genshin('100958637')
