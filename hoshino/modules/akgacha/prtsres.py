import re, json, time, os
from bs4 import BeautifulSoup
from contextlib import closing

from hoshino.config import RES_DIR
from hoshino import aiorequests

halfdict ={}
icondict ={}

working_path = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
icon_dir = os.path.join(RES_DIR, "img","akgacha")
half_dir = os.path.join(RES_DIR, "img","akgacha","half")

os.makedirs(icon_dir, exist_ok=True)
os.makedirs(half_dir, exist_ok=True)

char_data = json.load(
    open(os.path.join(working_path, "character_table.json"), encoding="utf-8"))
gacha_data = json.load(
    open(os.path.join(working_path, "config.json"), encoding="utf-8"))


proxies={ 'http':'socks5h://127.0.0.1:1080',
               'https':'socks5h://127.0.0.1:1080'}

async def update_res(): 
    count=0
    print("- 更新res资源包...")
    chars = json.load(open(os.path.join(working_path, "character_table.json"), encoding="utf-8"))

    for k in chars.keys():
        name = chars[k]["name"]
        if not k.startswith("char"):
            pass

    r = await aiorequests.get('http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88')
    soup = BeautifulSoup(await r.text)
    for index in soup.find(id="mw-content-text").find_all('div'):
        try:
            if index["class"]==["smwdata"]:
                halfdict[index['data-cn']]=index['data-half']
                icondict[index['data-cn']]=index['data-icon']
        except:
            continue

    for key in halfdict:
        filelink = halfdict[key]
        name=str(key)

        id=''
        for k in chars.keys():
            if name == chars[k]["name"]:
                id=str(k)
                break
                
        if id == '':
            if name == '阿米娅(近卫)':
                id="char_1001_amiya2"
                pass
            else:
                print(f'{name}not found！')
                continue
            
        filename = f'{id}.png'
        png_path = os.path.join(half_dir, filename)
        if os.path.exists(png_path):
            continue
        print(" - 下载", png_path)
        png = await (await aiorequests.get(filelink, timeout=20)).content
        count+=1
        with open(png_path, 'wb') as f:
            f.write(png)

    for key in icondict:
        filelink = icondict[key]
        name=str(key)

        id=''
        for k in chars.keys():
            if name == chars[k]["name"]:
                id=str(k)
                break
                
        if id == '':
            if name == '阿米娅(近卫)':
                id="char_1001_amiya2"
                pass
            else:
                print(f'{name}not found！')
                continue
            
        filename = f'{id}.png'
        png_path = os.path.join(icon_dir, filename)
        if os.path.exists(png_path):
            continue
        png = await (await aiorequests.get(filelink, timeout=20)).content
        count+=1
        print(" - 下载", png_path)
        with open(png_path, 'wb') as f:
            f.write(png)
        
    return count


async def update_chara_db():
    print("- 更新 character_table...")
    global char_data
    try:
        res = await aiorequests.get("https://gitcdn.link/repo/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json", timeout=10)
    except:
        try:
            res = await aiorequests.get("https://gitcdn.link/repo/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json", timeout=10,proxies=proxies)
        except:
            try:
                res = await aiorequests.get("https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json", timeout=10)
            except:
                res = await aiorequests.get("https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json", timeout=10,proxies=proxies)
    new = await res.json()
    if new == char_data:
        return 0
    char_data = new
    with open(os.path.join(working_path, "character_table.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(char_data, indent=2, ensure_ascii=False))
    return 1


async def update_config():
    global gacha_data

    print("- 更新方舟卡池...")
    template = {"limited": False, "no_other_6": False, "favor": '',
                "open": '', "end": '', "up_6": [], "up_5": [], "up_4": [], "exclude": []}

    # get basic info

    chars = json.load(
        open(os.path.join(working_path, "character_table.json"), encoding="utf-8"))
    pool = {
        "star_6": [],
        "star_5": [],
        "star_4": [],
        "star_3": [],
        "other_chars": [],
        "recruit_chars": ["艾丝黛尔", "清流", "火神", "因陀罗"],
        "limited_chars": ["W", "年", "迷迭香", "夕","灰烬","霜华","闪击","浊心斯卡蒂"]
    }

    for k in chars.keys():
        name = chars[k]["name"]
        if not k.startswith("char"):
            pass
        elif chars[k]["itemObtainApproach"] != "招募寻访" or chars[k]["rarity"] < 2:
            pool["other_chars"].append(name)
        elif not name in (pool["recruit_chars"] + pool["limited_chars"]):
            pool["star_%d" % (chars[k]["rarity"]+1)].append(name)

    # get chara onlinetime
    try:
        res = await aiorequests.get('http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%8A%E7%BA%BF%E6%97%B6%E9%97%B4%E4%B8%80%E8%A7%88', timeout=10)
    except:
        res = await aiorequests.get('http://prts.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%8A%E7%BA%BF%E6%97%B6%E9%97%B4%E4%B8%80%E8%A7%88', timeout=10,proxies=proxies)
    text = await res.text
    text = text.replace('\n', '')
    ret = r'<tr><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><\/tr>'
    result = re.findall(ret, text)
    online = {}
    for chara in result:
        name = re.search('title="(.*?)"', chara[0]).group(1)
        onlinetime = time.mktime(time.strptime(chara[2], "%Y年%m月%d日 %H:%M"))
        online[name] = onlinetime

    # get limited gacha

    try:
        res = await aiorequests.get('http://prts.wiki/w/%E5%8D%A1%E6%B1%A0%E4%B8%80%E8%A7%88/%E9%99%90%E6%97%B6%E5%AF%BB%E8%AE%BF', timeout=10)
    except:
        res = await aiorequests.get('http://prts.wiki/w/%E5%8D%A1%E6%B1%A0%E4%B8%80%E8%A7%88/%E9%99%90%E6%97%B6%E5%AF%BB%E8%AE%BF', timeout=10,proxies=proxies)
    text = await res.text
    text = text.replace('\n', '')
    banner = {}
    limited = re.findall("<table(.*?)</table>", text)
    ret = r'<tr><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><\/tr>'
    result = re.findall(ret, limited[0])
    for gacha in result:
        name = re.search('title="(.*?)"', gacha[0]).group(1)
        name = name.replace('寻访模拟/', '')
        gachatime = re.search(
            '(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', gacha[1])
        if not gachatime:
            print(f"gacha{name}time format error!")
            continue
        opentime = gachatime.group(1)
        opentimestp = time.mktime(time.strptime(opentime, "%Y-%m-%d %H:%M"))
        endtime = gachatime.group(2)
        endtimestp = time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M"))
        exclude = []
        for star in [pool["star_6"], pool["star_5"], pool["star_4"], pool["star_3"]]:
            for chara in star:
                if chara not in online:
                    exclude.append(chara)
                    continue
                elif online[chara] > opentimestp:
                    exclude.append(chara)
        star6 = re.findall('title="(.*?)"', gacha[2])
        star5 = re.findall('title="(.*?)"', gacha[3])
        star4 = []
        starex = re.findall(
            '%E7%A8%80%E6%9C%89%E5%BA%A6_%E9%BB%84_(\d).png', gacha[3])
        for i in range(0, len(starex)):
            if starex[i] == '3':
                star4.append(star5[i])
        for item in star4:
            if item in star5:
                star5.remove(item)
        cur = template.copy()
        cur["limited"] = True
        cur["favor"] = star6[0]
        cur["open"] = opentimestp
        cur["end"] = endtimestp
        cur["up_6"] = star6
        cur["up_5"] = star5
        cur["up_4"] = star4
        print(name)
        cur["exclude"] = exclude
        banner[name] = cur

    # get timelimit gacha

    result = re.findall(ret, limited[1])
    for gacha in result:
        name = re.search('title="(.*?)"', gacha[0]).group(1)
        name = name.replace('寻访模拟/', '')
        gachatime = re.search(
            '(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', gacha[1])
        if not gachatime:
            print(f"gacha{name}time format error!")
            continue
        opentime = gachatime.group(1)
        opentimestp = time.mktime(time.strptime(opentime, "%Y-%m-%d %H:%M"))
        endtime = gachatime.group(2)
        endtimestp = time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M"))
        exclude = []
        for star in [pool["star_6"], pool["star_5"], pool["star_4"], pool["star_3"]]:
            for chara in star:
                if chara not in online:
                    exclude.append(chara)
                    continue
                elif online[chara] > opentimestp:
                    exclude.append(chara)
        star6 = re.findall('title="(.*?)"', gacha[2])
        star5 = re.findall('title="(.*?)"', gacha[3])
        star4 = []
        starex = re.findall(
            '%E7%A8%80%E6%9C%89%E5%BA%A6_%E9%BB%84_(\d).png', gacha[3])
        for i in range(0, len(starex)):
            if starex[i] == '3':
                star4.append(star5[i])
        for item in star4:
            if item in star5:
                star5.remove(item)
        cur = template.copy()
        cur["limited"] = False
        cur["no_other_6"] = True if "联合行动" in name else False
        cur["favor"] = star6[0] if len(star6) > 1 else ''
        cur["open"] = opentimestp
        cur["end"] = endtimestp
        cur["up_6"] = star6
        cur["up_5"] = star5
        cur["up_4"] = star4
        print(name)
        cur["exclude"] = exclude
        banner[name] = cur

    # get normal gacha
    textn=""
    for year in ["2021","2020","2019"]:
        url=f"http://prts.wiki/api.php?action=parse&format=json&page=%E5%8D%A1%E6%B1%A0%E4%B8%80%E8%A7%88%2F%E5%B8%B8%E9%A9%BB%E6%A0%87%E5%87%86%E5%AF%BB%E8%AE%BF%2F{year}"
        try:
            res2 = await aiorequests.get(url, timeout=10)
        except:
            res2 = await aiorequests.get(url, timeout=10, proxies=proxies)
        resj= await res2.json()
        text2=resj["parse"]["text"]["*"].replace('\n', '').replace('\\', '')
        text=text+text2

    ret2 = r'<tr><td>(\d*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><td>(.*?)<\/td><\/tr>'
    result2 = re.findall(ret2, text)
    for gacha in result2:
        gachaid = gacha[0]
        gachatime = re.search(
            '(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', gacha[2])
        if not gachatime:
            print(f"id{gachaid}time format error!")
            continue
        opentime = gachatime.group(1)
        opentimestp = time.mktime(time.strptime(opentime, "%Y-%m-%d %H:%M"))
        endtime = gachatime.group(2)
        endtimestp = time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M"))
        exclude = []
        for star in [pool["star_6"], pool["star_5"], pool["star_4"], pool["star_3"]]:
            for chara in star:
                if chara not in online:
                    exclude.append(chara)
                    continue
                elif online[chara] > opentimestp:
                    exclude.append(chara)
        star6 = re.findall('title="(.*?)"', gacha[3])
        star5 = re.findall('title="(.*?)"', gacha[4])
        star4 = []
        starex = re.findall(
            '%E7%A8%80%E6%9C%89%E5%BA%A6_%E9%BB%84_(\d).png', gacha[4])
        for i in range(0, len(starex)):
            if starex[i] == '3':
                star4.append(star5[i])
        for item in star4:
            if item in star5:
                star5.remove(item)
        cur = template.copy()
        cur["id"] = gachaid
        cur["favor"] = star6[-1] if len(star6) > 1 else ''
        cur["open"] = opentimestp
        cur["end"] = endtimestp
        cur["id"] = gachaid
        cur["up_6"] = star6
        cur["up_5"] = star5
        cur["up_4"] = star4
        print(gachaid)
        cur["exclude"] = exclude
        banner[f'普池#{gachaid}'] = cur

    new = {"banners": banner, "pool": pool}
    if new == gacha_data:
        return 0
    gacha_data = new
    with open(os.path.join(working_path, "config.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(gacha_data, indent=2, ensure_ascii=False))
    return 1
