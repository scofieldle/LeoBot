import requests
from urllib import request, response, error, parse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


def get(lane):
    """
    gets a tier list from a specified lane
    lane options:
            "TOP"
            "JUNGLE"
            "MID"
            "ADC"
            "SUPPORT"
    """
    lane = lane.upper()
    URL = "https://www.op.gg/champion/statistics"
    hdr = {"Accept-Language": "zh-CN,zh;q=0.8", 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    req = Request(URL,headers=hdr)
    html = request.urlopen(req)
    soup = BeautifulSoup(html, "html.parser")
    ranks = soup.find("table", {"class": "champion-index-table tabItems"})
    tbodyclass = "tabItem champion-trend-tier-" + lane
    tbody = ranks.find("tbody", {"class": tbodyclass})

    place, name, win_rate, ban_rate = [], [], [], []
    for tr in tbody.find_all("tr"):
        raw = tr.find_all("td")
        #data = {}
        #print(raw)
        place.append(raw[0].text.strip())
        name.append(raw[3].find("a").find("div").text.strip())
        win_rate.append(raw[4].text.strip())
        ban_rate.append(raw[5].text.strip())

    return place, name, win_rate, ban_rate


def display_header(lane):
    """
    Displays table headers and lables for tier lists
    """
    outps = ""
    if (lane == "all"):
        for i in ["top", "jungle", "mid", "adc", "support"]:
            display_header(i)
    else:
        outps += lane.upper() + " TIER LIST\n\nTier\t\tName\t\tWin Rate\tBan Rate\n"
    return outps


def display(place, name, win_rate, ban_rate, lane):
    """
    #Displays data returned from tier lists
    print(raw)
    """
    outps = display_header(lane)
    for i in range(0, len(place)):
        if len(name[i]) >= 4:
            outps += place[i] + "\t\t" + name[i] + "\t" + win_rate[i] + "\t\t" + ban_rate[i] + "\n"
        else:
            outps += place[i] + "\t\t" + name[i] + "\t\t" + win_rate[i] + "\t\t" + ban_rate[i] + "\n"
    return outps
