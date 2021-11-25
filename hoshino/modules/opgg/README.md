# opgg 插件 for HoshinoBot

移植、“汉化”：ellye
触发前缀：opgg
（直接发 opgg 就可以看到使用帮助了）
以下是原项目 readme

# OPGG Scraper

This is a simple python scraper to pull down data from [opgg](https://op.gg).

Currently supports tier list for all lanes as well as skill orders for a specified champion in a specified lane.

This is also based on very specific formatting of opgg's website, so a redesign by them could break this at any time.

It is also exposed as an api at [lol.lukegreen.xyz](http://lol.lukegreen.xyz)

## Usage

```
$ python scrape.py <options>
```

| Command | Modifiers         | Description                                        |
| ------- | ----------------- | -------------------------------------------------- |
| -t      | all               | Display tier list of all lanes                     |
|         | adc               | Display adc tier list                              |
|         | jungle            | Display jungle tier list                           |
|         | support           | Display mid tier list                              |
|         | support           | Display support tier list                          |
|         | top               | Diplay top lane tier list                          |
| -so     | {champion} {lane} | Display skill orders for a given champion and lane |
| -b      | {champion} {lane} | Display optimal builds                             |
| -r      | {champion} {lane} | Display optimal runes                              |

## Current TODOs:

-   ~~get data for best runes~~

## Things I have learned

-   Examining HTML structure for relevant data
-   Use Beautiful Soup to make scraping easier
