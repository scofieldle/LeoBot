## 币安
本插件用于动态监测币安上各种货币涨跌情况

**本项目基于AGPL v3协议开源，由于项目特殊性，禁止基于本项目的任何商业行为**

## 配置方法
1. pip安装py文件中import的库
2. 注册币安账号
3. 获取币安api，方法请自行百度
4. 文件夹放入hoshino/modules下面，并在config中添加模块

## 命令
[币安查询 xxx] [币安价格 xxx] 查询币种当前美元价
[币安提醒 xxx 价格1 价格2] 设置币种价格提醒
[取消币安提醒 xxx] 取消币种价格提醒
[币安k线 xxx] 查看币种一日内k线图
[币安推送 xxx] 将指定币种加入推送队列，只有管理员才可以
[取消币安推送 xxx] 取消指定币种的推送