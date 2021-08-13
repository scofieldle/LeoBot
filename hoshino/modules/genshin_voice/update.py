import os
from collections import defaultdict

import requests, re
import ujson as json
from lxml import etree

characters = []
char_voice = defaultdict(dict)


def main():
    print("start updating voice list...")
    try:
        data = requests.get("https://genshin.honeyhunterworld.com/db/char/characters/?lang=CHS", timeout=10)
    except Exception as e:
        print("get characters list failed:", e)
        return
    if data.status_code != 200:
        print("get characters list failed, HTTP", data.status_code)
        return
    
    html = etree.HTML(data.text)
    html_data = html.xpath('//*[@id="post-349"]/div/div/div/div/a[1]')
    
    for i in range(len(html_data)):
        if html_data[i].attrib["href"].replace("/db/char/", "") == "characters/?lang=CHS":
            pass
        else:
            characters.append(html_data[i].attrib["href"].replace("/db/char/", "").replace("/?lang=CHS", ""))
    
    my_re = re.compile(r'[A-Za-z]',re.S)
    for name in characters:
        try:
            data = requests.get(f"https://genshin.honeyhunterworld.com/db/char/{name}/?lang=CHS", timeout=10)
        except Exception as e:
            print("get", name, 'voice list failed,', e)
            continue
        if data.status_code != 200:
            print("get", name, 'voice list failed, HTTP', data.status_code)
            continue
        
        html = etree.HTML(data.text)
        html_data = html.xpath("//td[@colspan=5][@style='color: #e5c302']")
        
        for i in range(len(html_data)):
            textget = html_data[i].text
            textget2 = textget.split('"')
            if len(textget2) == 1:
                textget = f'"{textget}"'
                pass
            else:
                textget = f'"{textget2[1]}"'
            
            html_data2 = html.xpath(f"""//td[contains(text(),{textget})]/../..//div[@class='audio_cont']""")
            
            for ii in range(len(html_data2)):
                char_name = name
                if 'travel' in char_name:
                    continue
                action = html_data[i].text
                if re.findall(my_re,action):
                    continue
                language = html_data2[ii].attrib['data-audio'][-2:]
                if action in char_voice[char_name]:
                    char_voice[char_name][action][
                        language] = f"https://genshin.honeyhunterworld.com/audio/{html_data2[ii].attrib['data-audio']}.wav"
                else:
                    char_voice[char_name][action] = {}
                    char_voice[char_name][action][
                        language] = f"https://genshin.honeyhunterworld.com/audio/{html_data2[ii].attrib['data-audio']}.wav"
    
    print("updating local file...")
    
    with open(os.path.join(os.path.dirname(__file__), 'char_voice.json'), 'w', encoding='utf-8') as f:
        json.dump(char_voice, f, ensure_ascii=False,
                  indent=2, escape_forward_slashes=False, sort_keys=True)
    
    print("complete.")


if __name__ == "__main__":
    main()
