from bs4 import BeautifulSoup as bs
import asyncio, random
from hoshino import Service,aiorequests

ciliwang = {
    "磁力猫":["https://clm134.xyz/", "https://clm126.xyz/", "https://clm129.xyz/", "https://clm130.xyz/", "https://clm131.xyz/", "https://clm132.xyz/", "https://clm133.xyz/"],
    "btsow":["https://btsow.rest/"],
    "种子搜":["https://zhongziso50.xyz/"],
    "磁力蜘蛛":["https://www.btmovi.co/"], 
}

async def clm_crawler(tag):
    url = ciliwang.get("磁力猫")[0]
    try:
        geturl = await aiorequests.get(url+f"search-{tag}-0-0-1.html", timeout = 6)
    except:
        return []
    count = 1
    while geturl.status_code != 200:
        url = ciliwang.get("磁力猫")[count]
        geturl = await aiorequests.get(url+f"search-{tag}-0-0-1.html", timeout = 6)
        count += 1
        if count == 7:
            stat = "bad"
            return stat
    reqs = await geturl.text
    title_list, magnet_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    box_soup = soup.findAll(name = "div", class_ = "ssbox")
    for i in box_soup:
        title = i.find(name = "div", class_ = "title").a
        sbar = i.find(name = "div", class_ = "sbar")
        title_text = title.text
        title_list.append(title_text.replace(tag, f"『{tag}』"))
        sbar_span = sbar.findAll(name = "span")
        info = ""
        for span in sbar_span:
            if span.text == "[磁力链接]":
                magnet = span.a.get("href")
                magnet_list.append(magnet)
                continue
            info += span.text + " "
        info_list.append(info)

    mes_list = []
    mes_list.append({
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"以下搜索结果来自于磁力猫({url})"
                        }
                })
    for i in range(len(title_list)):
        data = {
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"{title_list[i]}\n{magnet_list[i]}\n{info_list[i]}"
                        }
                }
        mes_list.append(data)
    return mes_list

async def btsow_crawler(tag):
    url = ciliwang.get("btsow")[0]
    try:
        geturl = await aiorequests.get(url+f"search/{tag}/page/1", timeout = 6)
    except:
        return []
    if geturl.status_code != 200:
        stat = "bad"
        return stat
    reqs = await geturl.text
    magnet_list, title_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    try:
        data = soup.find(name = "div", class_ = "data-list")
        row_list = data.findAll(name = "div", class_ = "row")
    except:
        return title_list
    for content in row_list:
        if len(content.get("class")) == 1 and content.get("class")[0] == 'row':
            size = content.find(name = "div", class_ = "size").string
            href = content.a.get("href")
            title = content.a.get("title")
            magnet_list.append(href.replace("//btsow.rest/magnet/detail/hash/", "magnet:?xt=urn:btih:"))
            title_list.append(title.replace(tag, f"『{tag}』"))
            info_list.append(f"大小：{size}")
        else:
            continue

    mes_list = []
    mes_list.append({
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"以下搜索结果来自于btsow({url})"
                        }
                })
    for i in range(len(title_list)):
        data = {
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"{title_list[i]}\n{magnet_list[i]}\n{info_list[i]}"
                        }
                }
        mes_list.append(data)
    return mes_list

async def zzs_crawler(tag):
    url = ciliwang.get("种子搜")[0]
    try:
        geturl = await aiorequests.get(url+f"list/{tag}/1", timeout = 6)
    except:
        return []
    if geturl.status_code != 200:
        stat = "bad"
        return stat
    reqs = await geturl.text
    title_list, magnet_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    table_list = soup.findAll(name = "table", class_ = "table table-bordered table-striped")
    for table in table_list:
        tr_list = table.findAll(name = "tr")
        title = tr_list[0].a.text
        title_list.append(title.replace(tag, f"『{tag}』"))
        magnet = tr_list[1].a.get("href")
        magnet_list.append(magnet)
        info_td = tr_list[1].findAll(name = "td")
        info_text = ""
        for td in info_td:
            if td.get("class"):
                continue
            info_text += td.text + " "
        info_list.append(info_text)
    
    mes_list = []
    mes_list.append({
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"以下搜索结果来自于种子搜({url})"
                        }
                })
    for i in range(len(title_list)):
        data = {
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"{title_list[i]}\n{magnet_list[i]}\n{info_list[i]}"
                        }
                }
        mes_list.append(data)
    return mes_list

async def clzz_crawler(tag):
    url = "https://www.btmovi.co/"
    try:
        geturl = await aiorequests.get(url+f"so/{tag}_rel_1.html", timeout = 6)
    except:
        return []
    if geturl.status_code != 200:
        stat = "bad"
        return stat
    print(geturl.status_code)
    reqs = await geturl.text
    title_list, magnet_list, info_list = [],[],[]
    soup = bs(reqs, "lxml")
    item_list = soup.findAll(name = "div", class_ = "search-item")
    for item in item_list:
        if item.text == "没有找到记录！":
            return title_list
        itemtitle = item.find(name = "div", class_ = "item-title")
        itembar = item.find(name = "div", class_ = "item-bar")
        title = itemtitle.a.text
        title_list.append(title.replace(tag, f"『{tag}』"))
        magnet = itemtitle.a.get("href").replace("/bt/", "magnet:?xt=urn:btih:").replace(".html", "")
        magnet_list.append(magnet)
        bar_list = itembar.findAll(name = "span")
        info = ""
        for span in bar_list:
            if span.get("class"):
                continue
            info += span.text.strip() + " "
        info_list.append(info.replace("\n", "").replace("\t", ""))
        
    mes_list = []
    mes_list.append({
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"以下搜索结果来自于磁力蜘蛛({url})"
                        }
                })
    for i in range(len(title_list)):
        data = {
                "type": "node",
                "data": {
                    "name": "神秘代码机器人",
                    "uin": "2854196310",
                    "content":f"{title_list[i]}\n{magnet_list[i]}\n{info_list[i]}"
                        }
                }
        mes_list.append(data)
    return mes_list

sv = Service("磁力搜bot")

@sv.on_prefix("聚合搜索")
async def gether_search(bot, ev):
    tag = ev.message.extract_plain_text().strip()
    await bot.send(ev, "聚合搜索需要的时间较久，请耐心等待")
    result = await asyncio.gather(clm_crawler(tag),btsow_crawler(tag),zzs_crawler(tag),clzz_crawler(tag))
    engine1 = result[0]
    engine2 = result[1]
    engine3 = result[2]
    engine4 = result[3]

    if engine1 == "bad" or len(engine1) <= 1:
        engine1 = []
    elif engine2 == "bad" or len(engine2) <= 1:
        engine2 = []
    elif engine3 == "bad" or len(engine3) <= 1:
        engine3 = []
    elif engine4 == "bad" or len(engine4) <= 1:
        engine4 = []

    mes_list = engine1 + engine2 + engine3 + engine4
    if mes_list == []:
        await bot.send(ev, "无搜索结果，或引擎访问失败，请检查服务器日志")
        return
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=mes_list)

@sv.on_prefix("搜磁力")
async def engine_search(bot, ev):
    tag = ev.message.extract_plain_text().strip()
    mode = random.choice(["1","2","3","4"])
    engine = ""

    await bot.send(ev, "请等待搜索结果")
    if mode == "1":
        engine = await clm_crawler(tag)
    elif mode == "2":
        engine = await btsow_crawler(tag)
    elif mode == "3":
        engine = await zzs_crawler(tag)
    elif mode == "4":
        engine = await clzz_crawler(tag)

    if engine == "bad":
        await bot.send(ev, "该引擎访问失败，可能是炸了，请换个引擎")
        return
    if len(engine) <= 1:
        await bot.send(ev, "无搜索结果，或引擎访问失败，请检查服务器日志")
        return
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=engine)