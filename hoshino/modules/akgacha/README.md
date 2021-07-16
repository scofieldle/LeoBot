# akgacha
Arknights Gacha Simulator plugin for [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)

Author: 库兰 - NGA romanosovsky
GitHub与问题反馈: https://github.com/xulai1001/akgacha

更新日志
======
# 5.22 更新了联合行动池，和联合行动池不歪的判定。已知问题：发饼机抓不到最新一条微博，可能是微博api的问题。
# 4.29 更新了fes池，优化了发饼排版，可以自动折叠和显示动图了
# 3.18 更新普池，更新R6干员头像
# 3.3 修正一些问题，增加r6卡池测试
# 2.28 增加素材一图流查询
# 2.23 更新干员头像和新普池

使用方法
======
[@Bot 方舟十连] 明日方舟抽卡

[@Bot 方舟来一井] 300抽

[查看方舟卡池] 当前卡池信息

[切换方舟卡池] 更改卡池，如果不加卡池名则会列出当前卡池列表

[饼呢 x] 查看方舟官方微博消息

[蹲饼/取消蹲饼] 开启、关闭蹲饼推送

[方舟刷本效率] 显示素材本一图流 

安装
======
- 将本项目放在hoshino/modules/目录下
- res.zip为头像数据，解压在Hoshino根目录下(头像路径为res/img/akgacha/*.png)

说明
======
- 插件启动时会自动在后台进行蹲饼，但是推送到群需要手动开启（群聊发送"蹲饼"开启）
- 蹲饼的微博ID可以在__init__.py中自行设置，默认为方舟官微和海猫
- 卡池数据在config.json中，可以在项目目录下运行generate_config.py生成。（up谁需要自己填写）
- 程序内使用的游戏图片，仅用于更好地表现游戏资料，其版权属于 Arknights/上海鹰角网络科技有限公司。其他内容采用知识共享署名-非商业性使用-相同方式共享授权。

已知问题
======
- 如果碰到找不到json文件的问题，尝试调整代码的working_path字符串。这部分还在调整中
- 如果蹲饼报错或者不推送，尝试删除group_banner.json
- 如果报ssl错误，可以尝试升级requests库到最新版本
