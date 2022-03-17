import re
import requests
import calendar
import asyncio
import aiohttp
import time
from pathlib import Path

from bs4 import BeautifulSoup

#config
pool_range = range(1,243)


pooldict ={}

pool_dir = 'pool'
Path(pool_dir).mkdir(parents = True, exist_ok = True) # parents：如果父目录不存在，是否创建父目录。exist_ok：只有在目录不存在时创建目录，目录已存在时不会抛出异常。

headers={"accept-language": "ja"}

def get_data():
    global get_data_end_time, get_data_start_time
    get_data_start_time = time.time()
    urls = {}
    for id in pool_range:
        try:
            res=requests.get(f"https://bandori.party/gachas/{id}",headers=headers)
            if res.status_code==404:
                print(f"活动 ID={id} 不存在")
                continue
            soup = BeautifulSoup(res.text, features="lxml")

            poolid = id

            name = soup.find(string='タイトル').parent.parent.next_sibling.next_sibling.text
            name = name.replace("  ","").replace("\n","").replace("\t","").replace("Gacha","ガチャ")
            
            pooltype = soup.find(string='ガチャタイプ').parent.parent.next_sibling.next_sibling.text
            pooltype = pooltype.replace("  ","").replace("\n","").replace("\t","")
            if pooltype=="ドリームフェスティバル":
                print(f"pool {poolid} is a Fes pool, uplist might be imcomplete.")

            times = soup.findAll(attrs={'data-to-timezone':'Asia/Tokyo'})

            start = times[0].find(attrs={'class':'datetime'}).text
            month=re.match("(\w*)\s(\d*)\,\s(\d*)\s", start).group(1)
            day=re.match("(\w*)\s(\d*)\,\s(\d*)\s", start).group(2)
            year=re.match("(\w*)\s(\d*)\,\s(\d*)\s", start).group(3)
            month=list(calendar.month_name).index(month)
            start =f"{year}/{month}/{day}"

            end = times[1].find(attrs={'class':'datetime'}).text
            month=re.match("(\w*)\s(\d*)\,\s(\d*)\s", end).group(1)
            day=re.match("(\w*)\s(\d*)\,\s(\d*)\s", end).group(2)
            year=re.match("(\w*)\s(\d*)\,\s(\d*)\s", end).group(3)
            month=list(calendar.month_name).index(month)
            end =f"{year}/{month}/{day}"
            
            upcard = soup.find(attrs={'data-field':'cards'})
            cardlist = re.finditer(r"/ajax/card/(\d*)/", str(upcard))
            uplist = []
            for i in cardlist:
                uplist.append(i.group(1))
            
            pooldict[id]=[name,pooltype,start, end, uplist]

            image = soup.find(string='日本のサーバー').parent.parent.parent.a["href"]
            src = f"http:{image}"
            urls[str(id) + '.png'] = src # 通过使用新的索引键并为其赋值，可以将项目添加到字典中
            
            if not id % 10:
                print(f"added {id}")
                
        except Exception as e:
            print(f"下载链接获取失败 id={id}")
            print(e)
            continue # 继续指令，只能用于循环中。报错后可继续完成循环

    Path('data').mkdir(parents = True, exist_ok = True)
    with Path('data', 'bang_pool.csv').open('w', encoding='utf-8-sig') as f: # utf_8_sig，解决在写入csv文件中，出现乱码的问题
        f.write("id,name,type,start,end,up1,up2,up3\n")
        for item in pooldict:
            f.write(f"{item},")
            for attri in pooldict[item]:
                if type(attri)==list:
                    for up in attri:
                        f.write(f"{up},")
                else:
                    f.write(f"{attri},")
            f.write("\n")
    get_data_end_time = time.time()
    print(f'活动数据写入完成, 用时{get_data_end_time - get_data_start_time}秒')

    return urls

num = []
async def aiodownload(name, url):
    png_path = Path(pool_dir, name)
    if not png_path.exists():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                png_path.write_bytes(await resp.content.read())
                print(f'文件 {name} 下载成功')
                num.append(1)
    else:
        print(f'文件 {name} 已存在，不再进行下载')

# 主协程对象
async def main():
    main_start = time.time()

    urls = get_data()
    
    tasks = [aiodownload(k, v) for k, v in urls.items()] # 生成执行任务的列表。items()，返回包含每个键值对的元组的列表，通过使用items()函数遍历键和值
    await asyncio.wait(tasks)

    main_end = time.time()

    print(f'''
全部完成！！！
共用时{main_end - main_start}秒，其中下载用时{(main_end - main_start) - (get_data_end_time - get_data_start_time)}秒
共下载成功{len(num)}个文件，{len(urls) - len(num)}个文件未下载
'''.strip())

if __name__ == "__main__":
    asyncio.run(main()) # asyncio.run()，创建事件循环，运行一个协程，关闭事件循环。
