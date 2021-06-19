# pixiv_new

基于HoshinoBot v2和pixivpy3的P站插件, 从P站直接获取图片.

本项目地址 https://github.com/scofieldle/LeoBot/hoshino/modules/pixiv_new

## 注意事项

本插件图片存放位置为 `res/img/pixiv` , 使用前请保证HoshinoBot的 `RES_DIR` 已经正确配置,并手动创建`pixiv`文件夹.

本插件不配置随机涩图功能,如有需要请自行添加。

## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/scofieldle/LeoBot.git`

1.***获取refresh_token***,注册pixiv账号,cmd模式输入 python3 pixiv_auth.py login,自动打开的登录界面中,F12,打开Network界面,点击Preserve Log,Filter框中输入callback对日志进行过滤；然后登录pixiv,找到callback?xxx日志中的refresh_token。

1. 详细说明请在`https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362`上查看

1. 在本插件目录`config.json`和`config.json`中修改该配置文件,设置自己的<token>和其他选项, 除<token>以外都可保持默认值.

1. 在 `config/__bot__.py`的模块列表里加入 `pixiv_new`

1. 重启HoshinoBot

## 指令说明

> `插画搜索 xxx` : 获取收藏最多的关键词相关图片,由于pixivpy一次性获取图片较少,每次关键词搜索到的图片质量较差
> `插画画师 uid` : 获取画师前10张图片
> `插画画师 uid` : 获取画师前10张图片
> `插画相关 uid` : 获取图片相关的10张图片
> `插画日榜 [r18]` : 获取本日[r18]榜单前15张图片
> `插画周榜 [r18]` : 获取本周[r18]榜单前15张图片
> `插画月榜` : 获取本月榜单前15张图片,月榜无r18区别

### 以下指令仅限超级用户使用

> `chahua set 模块 设置值 [群号]` : 修改本群或指定群的设置, 以下为设置项 - 取值 - 说明:
  > `pixiv` : `on / off` 是否开启pixiv模块
  > `pixiv_r18` : `on / off` 是否开启pixiv_r18模块
  > `withdraw` : `n` 发出的图片在n秒后撤回,设置为0表示不撤回. 如果撤回功能异常, 请关闭bot宿主程序的分片发送功能.
> `chahua get [群号]` : 查看本群或指定群的模块开启状态

## 开源

本插件以AGPL-v3协议开源


## TODO

> 插画搜索可能还有问题,请斟酌使用(虽然说该插件搜索功能不重要)
> 在windows系统上获取到的refresh_token,在服务器上有时候可能auth失败,多尝试几次吧~~~
