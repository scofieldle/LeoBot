> @Author: 帕瑟芬妮  
> @Contact: leoli1998@126.com  
> @Date: 2020-12-29  
> 说明： 使用RSS和feedparser实现直播订阅 


## 安装  

---

解压缩至./HoshinoBot/hoshino/modules，路径如有不一致，记得自己修改config  
hoshino的config里面添加插件'live_notice'  
pip(pip3) install -r requirements.txt  



## 命令

添加直播订阅 直播平台 订阅名 房间id
删除直播订阅 直播平台 订阅名  
查看直播订阅  



example: 添加直播订阅 bilibili 帕瑟芬妮 8268666
         添加直播订阅 斗鱼 xxx xxx

***需要境外服务器，或者自己搭梯子***  

### 尝试失败的产物，rss更新过于不及时，后续可能考虑直接requests获取直播间的html分析（requests访问b站会被屏蔽）