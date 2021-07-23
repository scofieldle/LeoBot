# akgacha
Arknights Gacha Simulator plugin for [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)

Author: 库兰 - NGA romanosovsky
GitHub与问题反馈: https://github.com/xulai1001/akgacha

使用方法
======
[@Bot 方舟十连] 明日方舟抽卡

[@Bot 方舟来一井] 300抽

[查看方舟卡池] 当前卡池信息

[切换方舟卡池] 更改卡池，如果不加卡池名则会列出当前卡池列表

[方舟刷本效率] 显示素材本一图流 

安装
======
- 将本项目放在hoshino/modules/目录下
- res.zip为头像数据，解压在Hoshino根目录下(头像路径为res/img/akgacha/*.png)

说明
======
- 卡池数据在config.json中，可以在项目目录下运行generate_config.py生成。（up谁需要自己填写）
- 程序内使用的游戏图片，仅用于更好地表现游戏资料，其版权属于 Arknights/上海鹰角网络科技有限公司。其他内容采用知识共享署名-非商业性使用-相同方式共享授权。

已知问题
======
- 如果碰到找不到json文件的问题，尝试调整代码的working_path字符串。这部分还在调整中
- 如果报ssl错误，可以尝试升级requests库到最新版本
