from nonebot import *
import random, os, json, re, time, datetime
from hoshino import Service, aiorequests
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


#信息抓取源码来源于https://github.com/Womsxd/YuanShen_User_Info
sv = Service('ysInfo')
bot = get_bot()
ip_list = []

mhyVersion = "2.11.1"
client_type = "5"
cache_Cookie = ['account_id=156463045; cookie_token=YTCH757SbuwzA7kSl2vkKOypnyPd2Oi5BVnFAm9t;',
            'account_id=7250452; cookie_token=xjAbaDN6bYpicppuYUye5h8exJSoYxLHyPFdO25X;',
            'account_id=279914305; cookie_token=GHCeB7nMYup87e5SWIcCDyFFhBoNNFfVPDpGnGXM;',
            'cookie_token=TUyfX4KBhWvOMlB43ELBFNMB13Hf9YgL5sa5f2SG; account_id=274933782;',
            'cookie_token=a734qsu6wfVo2DXeN0m6f4hMwApn5HkLyuF2RCg8; account_id=8546718;',
            'cookie_token=SmebcKUbZVonSRY5h0fEFVXU35nInT8RurSiu3j4; account_id=286893444;']

FILE_PATH = os.path.dirname(__file__)
FONTS_PATH = os.path.join(FILE_PATH,'fonts')
FONTS_PATH = os.path.join(FONTS_PATH,'sakura.ttf')
PIC_PATH = os.path.join(FILE_PATH,'pic')
last_time = time.time()
lck = Lock()
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
pic_list = {}

def load_pic():
    global pic_list
    temp = os.listdir(PIC_PATH)
    for pic in temp:
        uid = pic.split('-')[0]
        pic_list[uid] = {}
        pic_list[uid]['pic_name'] = pic
        make_time = pic[10:-4]
        make_time = datetime.datetime.strptime(make_time,'%Y-%m-%d').date()
        pic_list[uid]['time'] = make_time

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
load_pic()

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

async def request_data(uid=0, api='index', character_ids=None, cookie=''):
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
        'Cookie': cookie
    }

    params = {"role_id": uid, "server": server}

    json_data = None
    fn = aiorequests.get
    base_url = 'https://api-takumi.mihoyo.com/game_record/app/genshin/api/%s'
    url = base_url % api + '?'
    if api == 'index':
        url += urlencode(params)
    elif api == 'character':
        fn = aiorequests.post
        json_data = {"character_ids": character_ids,"role_id": uid, "server": server}
        params = {}

    headers['DS'] = __get_ds__(params, json_data)
    req = ''
    if api == 'index':
        req = await fn(url=url, headers=headers, json=json_data, timeout=10)
    else:
        num = random.random()
        if num > 0.5:
            ip = random.choice(ip_list)
            try:
                print(f'使用了代理{ip}')
                req = await fn(url=url, headers=headers, json=json_data, timeout=10, proxies={'https':ip})
            except:
                print(f'代理{ip}访问失败了')
                ip_list.remove(ip)
                save_config()
                load_config()
                req = await fn(url=url, headers=headers, json=json_data, timeout=10)
        else:
            req = await fn(url=url, headers=headers, json=json_data, timeout=10)
    if req:
        return await req.text
    else:
        return

async def get_pic(url, size=None):
    """
    从网络获取图片，格式化为RGBA格式的指定尺寸
    """
    resp = await aiorequests.get(url, timeout = 10)
    if resp.status_code != 200:
        return None
    pic = Image.open(BytesIO(await resp.content))
    pic = pic.convert("RGBA")
    if size is not None:
        pic = pic.resize(size, Image.LANCZOS)
    return pic

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

async def JsonAnalysis(info, Uid, nickname, cookie, qid):
    global pic_list
    if info:
        data = json.loads(info)
        if data["retcode"] == 10001:
            return "Cookie错误/过期，请重置Cookie"
        if data["retcode"] != 0:
            return ("Api报错，返回内容为："+ info)
    else:
        return "UID输入错误 or 不存在"

    Character_List = data["data"]["avatars"]
    Character_ids = []
    for i in Character_List:
        Character_ids +=  [i["id"]]
    time.sleep(5)
    dataC = json.loads(await request_data(uid=Uid, api='character', character_ids=Character_ids, cookie=cookie))
    Character_datas = dataC["data"]["avatars"]
    
    #命之座及好感度
    PLAYER = os.path.join(FILE_PATH,'player')
    FETTER = os.path.join(FILE_PATH,'fetter')
    #获取角色数量，计算输出图片长度
    characternum = data["data"]["stats"]["avatar_number"]
    need_middle = math.ceil(characternum/6)
    middle_height = need_middle*390
    img_height = middle_height+1024
    #背景图片初始化
    IMG_PATH = os.path.join(FILE_PATH,'images')
    im = Image.new("RGB", (1454, img_height), (255, 255, 255))
    #头部背景图片插入
    base_img1 = os.path.join(IMG_PATH,'ysinfo_top.png')
    dtimg1 = Image.open(base_img1)
    dtbox1 = (0, 0)
    im.paste(dtimg1, dtbox1)
    #插入标题图片
    base_img2 = os.path.join(IMG_PATH,'ysinfo_center.png')
    dtimg2 = Image.open(base_img2)
    dtbox2 = (0, 837)
    im.paste(dtimg2, dtbox2)
    #插入角色部分背景
    base_img = os.path.join(IMG_PATH,'ysinfo_back.png')
    dtimg = Image.open(base_img)
    for num in range(need_middle):
        dtheight = 937 + int(num) * 390
        dtbox = (0, dtheight)
        im.paste(dtimg, dtbox)
    #插入底部背景
    base_img3 = os.path.join(IMG_PATH,'ysinfo_bottom.png')
    dtimg3 = Image.open(base_img3)
    dtbox3 = (0, img_height-100)
    im.paste(dtimg3, dtbox3)
    
    #插入尘歌壶3个洞天
    #翠黛峰
    base_img_c = os.path.join(IMG_PATH,'翠黛峰.png')
    dtimg_c = Image.open(base_img_c).convert('RGBA')
    dtimg_c = dtimg_c.resize((188, 188))
    dtbox_c = (1140, 116)
    im.paste(dtimg_c, dtbox_c, mask=dtimg_c.split()[3])
    #罗浮洞
    base_img_l = os.path.join(IMG_PATH,'罗浮洞.png')
    dtimg_l = Image.open(base_img_l).convert('RGBA')
    dtimg_l = dtimg_l.resize((188, 188))
    dtbox_l = (1140, 319)
    im.paste(dtimg_l, dtbox_l, mask=dtimg_l.split()[3])
    #清琼岛
    base_img_q = os.path.join(IMG_PATH,'清琼岛.png')
    dtimg_q = Image.open(base_img_q).convert('RGBA')
    dtimg_q = dtimg_q.resize((188, 188))
    dtbox_q = (1140, 522)
    im.paste(dtimg_q, dtbox_q, mask=dtimg_q.split()[3])
    
    #插入查询者信息
    #插入昵称、uid、随机角色头像
    url = f'http://q.qlogo.cn/headimg_dl?dst_uin={qid}&spec=640&img_type=jpg'
    img = await get_pic(url, (180, 180))
    if img:
        dtbox_t = (86, 67)
        im.paste(img, dtbox_t, mask=img.split()[3])
    
    draw = ImageDraw.Draw(im)
    #插入UID
    line = "UID:"+str(Uid)
    font = ImageFont.truetype(FONTS_PATH, 22)
    w, h = draw.textsize(line, font=font)
    draw.text(((753 - w) / 2, 113), line, font=font, fill = (0, 158, 61))
    #插入昵称
    font = ImageFont.truetype(FONTS_PATH, 34)
    w, h = draw.textsize(nickname, font=font)
    draw.text(((753 - w) / 2, 143), nickname, font=font, fill = (0, 0, 0))
    
    #插入等级
    level = '??'
    #wordlevel = math.floor( ( level - 15 ) / 5 )
    line = str(level)+"级"
    font = ImageFont.truetype(FONTS_PATH, 42)
    w, h = draw.textsize(line, font=font)
    draw.text(((1774 - w) / 2, 122), line, font=font, fill = (255, 255, 255))
    
    #插入世界等级
    #line = "世界等级"+str(wordlevel)
    #font = ImageFont.truetype(FONTS_PATH, 22)
    #w, h = draw.textsize(line, font=font)
    #draw.text(((1774 - w) / 2, 170), line, font=font, fill = (255, 255, 255))
    
    font = ImageFont.truetype(FONTS_PATH, 32)
    #活跃天数　　
    line = str(data["data"]["stats"]["active_day_number"])
    draw.text((305, 296), line, font=font, fill = (255, 255, 255))
    #成就
    line = str(data["data"]["stats"]["achievement_number"])
    draw.text((305, 344), line, font=font, fill = (255, 255, 255))
    #角色数量
    line = str(data["data"]["stats"]["avatar_number"])
    draw.text((305, 392), line, font=font, fill = (255, 255, 255))
    #深渊
    if data["data"]["stats"]["spiral_abyss"] != "-":
        line=data["data"]["stats"]["spiral_abyss"]
    else:
        line="没打"
    draw.text((305, 440), line, font=font, fill = (255, 255, 255))
    
    #普通宝箱　　
    line = str(data["data"]["stats"]["common_chest_number"])
    draw.text((620, 296), line, font=font, fill = (255, 255, 255))
    #精致
    line = str(data["data"]["stats"]["exquisite_chest_number"])
    draw.text((620, 344), line, font=font, fill = (255, 255, 255))
    #珍贵
    line = str(data["data"]["stats"]["precious_chest_number"])
    draw.text((620, 392), line, font=font, fill = (255, 255, 255))
    #华丽
    line = str(data["data"]["stats"]["luxurious_chest_number"])
    draw.text((620, 440), line, font=font, fill = (255, 255, 255))
    
    #风神曈　　
    line = str(data["data"]["stats"]["anemoculus_number"])
    draw.text((925, 296), line, font=font, fill = (255, 255, 255))
    #岩
    line = str(data["data"]["stats"]["geoculus_number"])
    draw.text((925, 344), line, font=font, fill = (255, 255, 255))
    #雷
    line = str(data["data"]["stats"]["electroculus_number"])
    draw.text((925, 392), line, font=font, fill = (255, 255, 255))
    
    font = ImageFont.truetype(FONTS_PATH, 26)
    Area_list = data["data"]["world_explorations"]
    for i in Area_list:
        if i["type"] == "Reputation":
            if i["name"]=='蒙德':
                #蒙德
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((400, 546), line, font=font, fill = (255, 255, 255))
                line = "Lv."+spaceWrap(str(i["level"]), 2)
                draw.text((400, 595), line, font=font, fill = (255, 255, 255))
            elif i["name"]=='璃月':
                #璃月
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((400, 699), line, font=font, fill = (255, 255, 255))
                line = "Lv."+spaceWrap(str(i["level"]), 2)
                draw.text((400, 749), line, font=font, fill = (255, 255, 255))
            elif i["name"]=='稻妻':
                #稻妻
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((915, 691), line, font=font, fill = (255, 255, 255))
                line = "Lv."+spaceWrap(str(i["level"]), 2)
                draw.text((915, 728), line, font=font, fill = (255, 255, 255))
        else:
            if i['name']=='龙脊雪山':
                line = spaceWrap(str(i["exploration_percentage"] / 10).replace("100.0", "100"), 4)+'%'
                draw.text((915, 546), line, font=font, fill = (255, 255, 255))
        if len(i["offerings"]) != 0:
            if i["offerings"][0]["name"]=='神樱眷顾':
                line = "Lv." + spaceWrap(str(i["offerings"][0]["level"]), 2)
                draw.text((915, 764), line, font=font, fill = (255, 255, 255))
            elif i["offerings"][0]["name"]=='忍冬之树':
                line = "Lv." + spaceWrap(str(i["offerings"][0]["level"]), 2)
                draw.text((915, 595), line, font=font, fill = (255, 255, 255))
    
    #尘歌壶
    if len(data["data"]["homes"]) != 0:
        Home_List = data["data"]["homes"]
        line = "尘歌壶 Lv."+ str(Home_List[0]["level"])
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 75), line, font=font, fill = (255, 255, 255))
        
        #尘歌壶3个洞天
        homeworld_list = []
        #有解锁的洞天
        for i in Home_List:
            homeworld_list.append(i["name"])
            if i['name']=='翠黛峰':
                line = i['name']
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 165), line, font=font, fill = (242, 196, 127))
                
                line = "洞天等级"
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 203), line, font=font, fill = (250, 245, 207))
                
                line = i['comfort_level_name']
                font = ImageFont.truetype(FONTS_PATH, 24)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 232), line, font=font, fill = (255, 255, 255))
            elif i['name']=='罗浮洞':
                line = i['name']
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 368), line, font=font, fill = (242, 196, 127))
                
                line = "洞天等级"
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 406), line, font=font, fill = (250, 245, 207))
                
                line = i['comfort_level_name']
                font = ImageFont.truetype(FONTS_PATH, 24)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 435), line, font=font, fill = (255, 255, 255))
            elif i['name']=='清琼岛':
                line = i['name']
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 571), line, font=font, fill = (242, 196, 127))
                
                line = "洞天等级"
                font = ImageFont.truetype(FONTS_PATH, 30)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 609), line, font=font, fill = (250, 245, 207))
                
                line = i['comfort_level_name']
                font = ImageFont.truetype(FONTS_PATH, 24)
                w, h = draw.textsize(line, font=font)
                draw.text(((2474 - w) / 2, 638), line, font=font, fill = (255, 255, 255))
        #未解锁的洞天
        if '翠黛峰' not in homeworld_list:
            line = '翠黛峰'
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 165), line, font=font, fill = (242, 196, 127))
            
            line = "洞天等级"
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 203), line, font=font, fill = (250, 245, 207))
            
            line = '未解锁'
            font = ImageFont.truetype(FONTS_PATH, 24)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 232), line, font=font, fill = (255, 255, 255))
        if '罗浮洞' not in homeworld_list:
            line = '罗浮洞'
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 368), line, font=font, fill = (242, 196, 127))
            
            line = "洞天等级"
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 406), line, font=font, fill = (250, 245, 207))
            
            line = '未解锁'
            font = ImageFont.truetype(FONTS_PATH, 24)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 435), line, font=font, fill = (255, 255, 255))
        if '清琼岛' not in homeworld_list:
            line = '清琼岛'
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 571), line, font=font, fill = (242, 196, 127))
            
            line = "洞天等级"
            font = ImageFont.truetype(FONTS_PATH, 30)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 609), line, font=font, fill = (250, 245, 207))
            
            line = '未解锁'
            font = ImageFont.truetype(FONTS_PATH, 24)
            w, h = draw.textsize(line, font=font)
            draw.text(((2474 - w) / 2, 638), line, font=font, fill = (255, 255, 255))
            
        #摆设
        line = "摆件:" + str(Home_List[0]["item_num"])
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 730), line, font=font, fill = (255, 255, 255))
        #最大仙力
        line = '仙力:' + str(Home_List[0]["comfort_num"])
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 770), line, font=font, fill = (255, 255, 255))
    else:
        line = '翠黛峰'
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 165), line, font=font, fill = (242, 196, 127))
        
        line = "洞天等级"
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 203), line, font=font, fill = (250, 245, 207))
        
        line = '未解锁'
        font = ImageFont.truetype(FONTS_PATH, 24)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 232), line, font=font, fill = (255, 255, 255))

        line = '罗浮洞'
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 368), line, font=font, fill = (242, 196, 127))
        
        line = "洞天等级"
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 406), line, font=font, fill = (250, 245, 207))
        
        line = '未解锁'
        font = ImageFont.truetype(FONTS_PATH, 24)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 435), line, font=font, fill = (255, 255, 255))

        line = '清琼岛'
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 571), line, font=font, fill = (242, 196, 127))
        
        line = "洞天等级"
        font = ImageFont.truetype(FONTS_PATH, 30)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 609), line, font=font, fill = (250, 245, 207))
        
        line = '未解锁'
        font = ImageFont.truetype(FONTS_PATH, 24)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 638), line, font=font, fill = (255, 255, 255))
        
        #摆设
        line = "摆件:0"
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 730), line, font=font, fill = (255, 255, 255))
        #最大仙力
        line = '仙力:0'
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        draw.text(((2474 - w) / 2, 770), line, font=font, fill = (255, 255, 255))
    
    zb_list = []
    for l in range(need_middle):
        for i in range(6):
            zb_list.append([l,i])
    
    jishu = 0
    ICON_PATH = os.path.join(FILE_PATH,'icon')
    for i in Character_datas:
        #937 390xl 50 200 30 230xi
        #计算位置
        z_left = 50+230*zb_list[jishu][1]
        z_top = 937+390*zb_list[jishu][0]
        #插入底图
        base_img = os.path.join(IMG_PATH,'card_content.png')
        dtimg = Image.open(base_img).convert('RGBA')
        dtbox = (z_left, z_top)
        im.paste(dtimg, dtbox, mask=dtimg.split()[3])
        
        weapon = i["weapon"]
        if i["name"] == "旅行者":
            if i["image"].find("UI_AvatarIcon_PlayerGirl") != -1:
                name = str("荧")
            elif i["image"].find("UI_AvatarIcon_PlayerBoy") != -1:
                name = str("空")
            else:
                name = str("旅行者")
        else:
            name = str(i["name"])
        
        #插入角色头像
        picname = str(name) +".png"
        icon_name = os.path.join(ICON_PATH,picname)
        if os.path.exists(icon_name):
            img = Image.open(icon_name).convert('RGBA')
        else:
            urllib.request.urlretrieve(i['icon'], icon_name)
            img = Image.open(icon_name).convert('RGBA')
        img = img.resize((200, 200))
        dtbox = (z_left, z_top)
        im.paste(img, dtbox, mask=img.split()[3])
        
        #插入角色命座
        line = str(i["actived_constellation_num"])
        i_con = Image.open(os.path.join(PLAYER, f'命之座{line}.png'))
        i_con = i_con.resize((43, 43))
        mz_left = z_left + 158
        mz_top = z_top
        mzbox = (mz_left, mz_top)
        im.paste(i_con, mzbox, mask=i_con.split()[3])
        
        #插入角色属性
        elementname = str(i["element"]) +".png"
        element_img = os.path.join(IMG_PATH,elementname)
        eleimg = Image.open(element_img).convert('RGBA')
        eleimg = eleimg.resize((30, 30))
        ele_left = z_left + 5
        els_top = z_top + 7
        elebox = (ele_left, els_top)
        im.paste(eleimg, elebox, mask=eleimg.split()[3])
        
        #插入角色姓名
        line = str(name)
        font = ImageFont.truetype(FONTS_PATH, 26)
        w, h = draw.textsize(line, font=font)
        name_max_width = (z_left+100)*2
        name_top = z_top + 215
        draw.text(((name_max_width - w) / 2, name_top), line, font=font, fill = (0, 0, 0))
        
        #插入角色等级
        line = 'Lv.' + spaceWrap(str(i["level"]), 2)
        font = ImageFont.truetype(FONTS_PATH, 26)
        level_left = z_left + 28
        level_top = z_top + 250
        draw.text((level_left, level_top), line, font=font, fill = (0, 0, 0))
        
        #插入角色好感度
        line = str(i["fetter"])
        i_fet = Image.open(os.path.join(FETTER, f'好感度{line}.png'))
        i_fet = i_fet.resize((45, 45))
        fetter_left = z_left + 135
        fetter_top = z_top + 242
        fetterbox = (fetter_left, fetter_top)
        im.paste(i_fet, fetterbox, mask=i_fet.split()[3])
        
        #插入武器图片
        weaponname = str(weapon["name"]) +".png"
        weapon_name = os.path.join(ICON_PATH,weaponname)
        if os.path.exists(weapon_name):
            weapon_img = Image.open(weapon_name).convert('RGBA')
        else:
            urllib.request.urlretrieve(weapon['icon'], weapon_name)
            weapon_img = Image.open(weapon_name).convert('RGBA')
        weapon_img = weapon_img.resize((60, 60))
        weapon_left = z_left + 9
        weapon_top = z_top + 283
        weaponbox = (weapon_left, weapon_top)
        im.paste(weapon_img, weaponbox, mask=weapon_img.split()[3])
        
        #插入武器名称
        line = str(weapon["name"])
        font = ImageFont.truetype(FONTS_PATH, 18)
        weaponname_left = z_left + 73
        weaponname_top = z_top + 291
        draw.text((weaponname_left, weaponname_top), line, font=font, fill = (0, 0, 0))
        
        #插入武器等级精炼
        line = 'Lv.' + str(weapon["level"]) + " 精炼." + str(weapon["affix_level"])
        font = ImageFont.truetype(FONTS_PATH, 18)
        weaponlv_left = z_left + 73
        weaponlv_top = z_top + 320
        draw.text((weaponlv_left, weaponlv_top), line, font=font, fill = (0, 0, 0))
        
        jishu = jishu + 1
        
    nowtime = str(datetime.datetime.now().date())
    pic_name = Uid + '-' + nowtime + '.png'
    save_path = os.path.join(PIC_PATH, pic_name)
    im.save(save_path)
    if Uid in pic_list.keys():
        os.remove(os.path.join(PIC_PATH,pic_list[Uid]['pic_name']))
    load_pic()

    bio  = io.BytesIO()
    im.save(bio, format='PNG')
    base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
    mes  = f"[CQ:image,file={base64_str}]"
    return mes
    
@sv.on_prefix('原神信息')
async def genshin(bot, ev):
    global lck, last_time, pic_list
    now_time = time.time()
    uid = ev.message.extract_plain_text()
    qid = ev.user_id
    sender = ev.sender
    if now_time - last_time < 10:
        await bot.send(ev, '请求过于频繁！')
        return
    while not lck.locked():
        with lck:
            if uid.isdigit() and (len(uid) == 9):
                if uid in pic_list.keys():
                    nowtime = datetime.datetime.now().date()
                    if (nowtime - pic_list[uid]['time']).days < 4:
                        image = Image.open(os.path.join(PIC_PATH, pic_list[uid]['pic_name']))
                        bio = BytesIO()
                        image.save(bio, format='PNG')
                        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
                        mes = f"[CQ:image,file={base64_str}]"
                        await bot.send(ev, f"距离上次查询{str((nowtime - pic_list[uid]['time']).days)}天，使用前次图片")
                        await bot.send(ev, mes)
                        return
                cookie = random.choice(cache_Cookie)
                nickname = sender["card"] or sender["nickname"]
                try:
                    await bot.send(ev, '正在前往米游社查询信息')
                    if (uid[0] == "1") or (uid[0] == "2"):
                        mes = await JsonAnalysis(await request_data(uid=uid, cookie=cookie), uid, nickname, cookie, qid)
                    elif (uid[0] == "5"):
                        mes = await JsonAnalysis(await request_data(uid=uid, cookie=cookie), uid, nickname, cookie, qid)
                except Exception as e:
                    print(e)
                    await bot.send(ev, f'米游社无法查询到此uid\n{e}')
                    last_time = time.time()
                    return
                await bot.send(ev, mes)
                last_time = time.time()
            else:
                await bot.send(ev, 'UID输入有误！', at_sender=True)
        break

@sv.on_fullmatch('更新代理池')
async def up_ip_list(bot, ev):
    await bot.send(ev, '开始更新')
    for i in range(20):
        url = f'https://ip.ihuan.me/?page={i}'
        await get_ip_list(url)
        time.sleep(0.5)
    save_config()
    load_config()
    await bot.send(ev, f'更新完成，目前代理池IP数量为{len(ip_list)}')

@sv.scheduled_job('interval', minutes=5)
async def schedule_ip_list():
    if len(ip_list) < 20:
        for i in range(20):
            url = f'https://ip.ihuan.me/?page={i}'
            await get_ip_list(url)
            time.sleep(0.5)
        save_config()
        load_config()
    return
