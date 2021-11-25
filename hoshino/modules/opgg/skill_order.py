import requests
from urllib import request, response, error, parse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


def get(lane, name):
    """
    Gets skill order of specific champion and lane
    """
    URL = "https://www.op.gg/champion/" + name + "/statistics/" + lane
    hdr = {"Accept-Language": "zh-CN,zh;q=0.8", 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    req = Request(URL,headers=hdr)
    html = request.urlopen(req)
    soup = BeautifulSoup(html, "html.parser")
    skills = soup.find("table", {"class": "champion-skill-build__table"})
    tbody = skills.find("tbody")
    tr = tbody.find_all("tr")[1]
    skill_table = []
    for td in tr.find_all("td"):
        if td.text.strip() == 'Q' or td.text.strip() == 'W' or td.text.strip() == 'R' or td.text.strip() == 'E':
            skill_table.append(td.text.strip())

    return skill_table


def display(skills):
    """
    Displays skill order of a specific champion and lane
    """
    outstring = ""
    for i in skills:
        outstring = outstring + i + "->"
    return outstring[:-2]
