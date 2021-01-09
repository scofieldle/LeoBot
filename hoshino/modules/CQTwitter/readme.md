> @Author: 帕瑟芬妮  
> @Contact: leoli1998@126.com  
> @Date: 2020-12-29  
> 说明： 使用RSS和feedparser实现twitter关注和转发推文，无需twitter开发者账号  


## 安装  

---

解压缩至./HoshinoBot/hoshino/modules，路径如有不一致，记得自己修改config  
hoshino的config里面添加插件'CQTwitter'  
pip(pip3) install -r requirements.txt  



## 命令

添加订阅 订阅名 `twitter全名`  
删除订阅 订阅名  
查看所有订阅  



example: 添加订阅 帕瑟芬妮 scofieldle2

***需要境外服务器，或者自己搭梯子***  

## rss更新可能不及时，发推频繁的人会出现漏掉推送的情况，可以自己修改`rsshub`中第214行range()内容