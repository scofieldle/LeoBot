import requests
from urllib import request, response, error, parse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


def get(lane, name, proxy):
    """
    Gets build for a champion in a specific lane
    """
    build = [
        ('出门装1', []),
        ('出门装2', []),
        ('中期1', []),
        ('中期2', []),
        ('中期3', []),
        ('中期4', []),
        ('中期5', []),
        ('鞋子1', []),
        ('鞋子2', []),
        ('鞋子3', [])
    ]
    URL = "https://www.op.gg/champion/" + name + "/statistics/" + lane
    hdr = {"Accept-Language": "zh-CN,zh;q=0.8", 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    if proxy:
        try:
            req = Request(URL,headers=hdr, proxies={'https':proxy}, timeout=10)
        except:
            return
    else:
        req = Request(URL,headers=hdr)
    html = request.urlopen(req)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find_all("table", {"class": "champion-overview__table"})
    tbody = table[1].find("tbody")
    tr = tbody.find_all("tr", {"class": "champion-overview__row"})
    try:
        for i in range(0, 10):
            td = tr[i].find("td", {"class": "champion-overview__data"})
            ul = td.find("ul", {"class": "champion-stats__list"})
            li = ul.find_all("li")
            for j in li:
                try:
                    mystr = j['title']
                    start = mystr.find('>') + 1
                    end = mystr.find('<', 1)
                    build[i][1].append(mystr[start:end])
                except KeyError:
                    pass
    except:
        pass
    return build


def display(data):
    outps = ""
    for i in data:
        build_items = ''
        for j in i[1]:
            build_items += j
            build_items += ', '
        outps += i[0] + ' :  ' + build_items[:len(build_items) - 2] + "\n"
        #print(i[0], ': ', build_items[:len(build_items) - 2])
    return outps
