# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SpMoviesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    slink = scrapy.Field()

class SpMovieItem(scrapy.Item):
    imdb = scrapy.Field()   # 豆瓣id
    dbid = scrapy.Field()   # 豆瓣id
    title = scrapy.Field()  # 片名
    imgs = scrapy.Field()   # 图片
    year = scrapy.Field()   # 年份
    directors = scrapy.Field()  # 导演
    actors = scrapy.Field() # 演员
    subtypes = scrapy.Field()   # 类型风格
    area = scrapy.Field()    # 地域
    alias = scrapy.Field()      # 别名 
    summary = scrapy.Field()    # 详情简介
    genres = scrapy.Field()  # 类型：电影、电视剧、综艺、动漫 
    slname = scrapy.Field()
    slcode = scrapy.Field()
    slink = scrapy.Field()  # 源链接
    eplinks = scrapy.Field()    # 分集播放地址
    newtoday = scrapy.Field()   # 上新日期

