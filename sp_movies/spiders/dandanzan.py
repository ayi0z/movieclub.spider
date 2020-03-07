# -*- coding: utf-8 -*-
import scrapy
from sp_movies.items import SpMovieItem
from scrapy_splash import SplashRequest
from urllib.parse import quote
import json
from scrapy.http.headers import Headers
import requests


class DandanzanSpider(scrapy.Spider):
    name = 'dandanzan'
    allowed_domains = ['www.dandanzan.com']
    start_urls = [
        'https://www.dandanzan.com/dianying/',
        'https://www.dandanzan.com/dianshiju/',
        # 'https://www.dandanzan.com/zongyi/',
        # 'https://www.dandanzan.com/dongman/'
    ]
    genres = {
        'dianying':1,
        'dianshiju':2,
        'dongman':3,
        'zongyi':4
    }

    # scrapy crawl dandanzan -a <pc=1>
    # 不带pc参数 => 自动加载下一页
    # 带pc参数 => 订阅更新模式
    # pc参数是数字 => 更新pc指定页数
    def __init__(self, pc=None, *args, **kwargs):
        super(DandanzanSpider, self).__init__(*args, **kwargs)
        self.isAutoLoadMode = False
        if pc == None:
            self.isAutoLoadMode = True
        else:
            pc = pc.strip()
            pc = int(pc) if pc.isdigit() else 0
            if pc > 1:
                for x in range(2, int(pc) + 1):
                    self.start_urls.append('https://www.dandanzan.com/dianying/index_%s.html' % x)
                    self.start_urls.append('https://www.dandanzan.com/dianshiju/index_%s.html' % x)
                    # self.start_urls.append('https://www.dandanzan.com/zongyi/index_%s.html' % x)
                    # self.start_urls.append('https://www.dandanzan.com/dongman/index_%s.html' % x)
                self.start_urls.reverse()

    # 解析 影片 列表页面
    def parse(self, response):
        for li_a in response.css('div.lists-content ul li'):
            mc_url = li_a.css('a::attr(href)').extract_first()
            if mc_url is not None:
                yield response.follow(mc_url, callback=self.parse_moviecontent)

        if self.isAutoLoadMode:
            # 自动加载模式： 自动抓取‘下一页’链接
            next_page = response.css('li.next-page a::attr(href)').extract_first()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
    

    # 解析每一个 影片 详细页面的数据
    def parse_moviecontent(self, response):
        mItem = SpMovieItem()
        subtypes = response.xpath(u'//header/div[@class="product-excerpt"][text()="类型："]/span/a/text()').extract()
        # isQs = subtypes.split(',').count('情色') > 0
        # if isQs :
        #     return
        mItem['imgs'] = response.xpath('//header/img[@class="thumb"]/@src').extract_first()
        mItem['title'] = response.xpath('//header/h1[@class="product-title"]/text()').extract_first()
        mItem['year'] = response.xpath('//header/h1[@class="product-title"]/span[1]/text()').re_first(r'\d+')
        mItem['directors'] = response.xpath(u'//header/div[@class="product-excerpt"][text()="导演："]/span/a/text()').extract()
        mItem['actors'] = response.xpath(u'//header/div[@class="product-excerpt"][text()="主演："]/span/a/text()').extract()
        mItem['subtypes'] = subtypes
        mItem['area'] = response.xpath(u'//header/div[@class="product-excerpt"][text()="制片国家/地区："]/span/a/text()').extract()
        alias = response.xpath(u'//header/div[@class="product-excerpt"][text()="又名："]/span/text()').extract_first()
        mItem['alias'] = alias.split(' / ') if alias else []
        mItem['summary'] = response.xpath(u'//header/div[@class="product-excerpt"][text()="剧情简介："]/span/text()').extract_first()
        mItem['slname'] = 'dandanzan'
        mItem['slcode'] = response.url.split('/')[-1].split('.')[-2]
        mItem['slink'] = response.url
        mItem['genres'] = self.genres[response.url.split('/')[-2]]
        mItem['eplinks'] = []
        for var in response.xpath('//script/text()').extract_first().split(';'):
            if '=' in var :
                var = var.strip()
                spl = var.find('=')
                key = var[0:spl]
                if key == 'var links':
                    value = var[spl+1:]
                    epurl = self.get_links(value.strip('\''))
                    epurl = json.loads(epurl)
                    for index, ep in enumerate(epurl):
                        if '$' in ep :
                            title, playurl = ep.split('$')[0:2]
                            mItem['eplinks'].append({
                                'epno' : index + 1,
                                'title' : title,
                                'playurl' : playurl,
                                'playgate': 'dybox',
                                'args': ''
                            })
                elif key == 'var id':
                    mItem['dbid'] = value
        mItem['imdb'] = ''
        mItem['newtoday'] = ''
        yield mItem 
    
    def get_links(self, links):
        splash_script='''
        function main(splash, args)
            assert(splash:autoload("http://dy.ayioz.com/js/crypto.js"))
            assert(splash:set_content("<html><body><h1>hello</h1></body></html>"))
            return splash:evaljs("get_links(\'"..args.js_source.."\')")
            -- return args.js_source
        end
        '''
        response = requests.post('http://0.0.0.0:8050/execute?lua_source='+quote(splash_script), json={'links':json.loads(links), 'ws':'www.dandanzan.com'}, headers={'Content-Type': 'application/javascript'})
        return response.text