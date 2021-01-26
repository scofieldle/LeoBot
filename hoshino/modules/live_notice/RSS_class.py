import re

class rss():
    # 定义基本属性
    platform = ''#直播平台
    url = ''  # 订阅地址
    group_id = []  # 订阅群组

    # 返回订阅链接
    def geturl(self, platform) -> str:
        if platform == 'bilibili':
            rsshub = 'https://live.bilibili.com/'
            return rsshub + self.url
        if platform == '斗鱼':
            rsshub = 'https://rsshub.app/douyu/room/'
            return rsshub + self.url
        
