# 一个基于 scrapy 的简单的爬虫示例
可为 [movieclub.pcweb](https://github.com/ayi0z/movieclub.pcweb) 和 [movieclub.wechat](https://github.com/ayi0z/movieclub.wechat) 提供视频链接资源

## 使用 mongodb
> STORGE_DRIVER = 'pymongo'

> /sp_movies/settings.py -> MONGO_URI & MONGO_DATABASE

## 使用 mysql
> STORGE_DRIVER = 'mysql.connector'

> /sp_movies/settings.py -> MYSQL_HOST & MYSQL_USER & MYSQL_PASSWD & MYSQL_DATABASE

> mysql 数据库表创建脚本: /movieclub.sql

## requirements：
```
    python: 3.7.1
    Scrapy: 1.6.0
    pymongo: 3.7.2  
    dnspython: 1.16.0
```

## run:
```
    cd <your-spider-folder>
    scrapy crawl <spider-name> -a pc=5
    // <spider-name> 爬虫名称: dandanzan
    // -a pc=抓取页数
```


