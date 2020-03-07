# -*- coding: utf-8 -*-
import scrapy
from sp_movies.items import SpMovieItem
from scrapy_splash import SplashRequest
from urllib.parse import quote
from urllib.parse import unquote
import json
from scrapy.http.headers import Headers
import requests
import re
import time
import datetime
import random
import string

import os
import sys 
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import wxsvr

class DililitvSpider(scrapy.Spider):
    name = '91mjw'
    allowed_domains = ['91mjw.com']
    start_urls = [
        'https://91mjw.com/all'
    ]
    genres = {
        'dianying':1,
        'all_mj':2,
        'cartoon':3,
        'zongyi':4,
        'jilupian':2
    }

    # scrapy crawl dililitv -a <pc=1>
    # 不带pc参数 => 自动加载下一页
    # 带pc参数 => 订阅更新模式
    # pc参数是数字 => 更新pc指定页数
    # pc = new => 今天+昨天两天更新
    def __init__(self, pc=None, *args, **kwargs):
        super(DililitvSpider, self).__init__(*args, **kwargs)
        self.isAutoLoadMode = 'normal'
        if pc == None:
            self.isAutoLoadMode = 'auto'
        elif pc.strip() == 'new':
            self.isAutoLoadMode = 'new'
            tcode = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            self.start_urls = [ 'https://91mjw.com/last-update?t=' + tcode ]
            # self.start_urls = [ 'https://91mjw.com/category/jilupian' ]
        else:
            pc = pc.strip()
            pc = int(pc) if pc.isdigit() else 0
            if pc > 1:
                for x in range(2, int(pc) + 1):
                    self.start_urls.append('https://91mjw.com/all/page/%s' % x)
                self.start_urls.reverse()

    # 解析 影片 列表页面
    def parse(self, response):
        today = str(datetime.date.today())
        yesterday = str(datetime.date.today() + datetime.timedelta(-1))
        # counter = 0
        for li_a in response.css('div.video-content div.m-movies article.u-movie'):
            mc_url = li_a.css('a::attr(href)').extract_first().strip()
            # debug
            # if mc_url is not None and counter < 1:
            #     counter = counter + 1
            exact = [
                # 'http://www.dililitv.com/gresource/1820',
                # 'http://www.dililitv.com/gresource/5341'
            ]
            if mc_url is not None and mc_url not in exact:
                # yield response.follow(mc_url, callback=self.parse_moviecontent_normal)
                if self.isAutoLoadMode == 'new':
                    meta_tags = li_a.css('div.meta span.tags::text').extract_first()
                    meta_tags = meta_tags.strip().split(' ')[0] if meta_tags else ''
                    if meta_tags == today:
                        yield response.follow(mc_url, callback=self.parse_moviecontent_today)
                    elif meta_tags == yesterday:
                        yield response.follow(mc_url, callback=self.parse_moviecontent_yesterday)
                else:
                    yield response.follow(mc_url, callback=self.parse_moviecontent_normal)

        if self.isAutoLoadMode == 'auto':
            # 自动加载模式： 自动抓取‘下一页’链接
            next_page = response.css('li.next-page a::attr(href)').extract_first()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
    def closed(self, reason):
        print(reason)
        if reason == 'finished':
            wxsvr.auto_todayupdate()

    
    def parse_moviecontent_today(self, response):
        mItem = SpMovieItem()
        mItem['newtoday'] = str(datetime.date.today())
        yield self.parse_moviecontent(response, mItem)

    def parse_moviecontent_yesterday(self, response):
        mItem = SpMovieItem()
        mItem['newtoday'] = str(datetime.date.today() + datetime.timedelta(-1))
        yield self.parse_moviecontent(response, mItem)

    def parse_moviecontent_normal(self, response):
        mItem = SpMovieItem()
        mItem['newtoday'] = ''
        yield self.parse_moviecontent(response, mItem)

    # 解析每一个 影片 详细页面的数据
    def parse_moviecontent(self, response, mItem):
        imgs = response.xpath('//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_img"]/img/@src').extract_first()
        title = re.search('《.+》', response.xpath('//head/title/text()').extract_first()).group()
        directors = response.xpath('//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="导演:"]/following-sibling::text()[1]').extract_first()
        actors = response.xpath('//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="主演:"]/following-sibling::text()[1]').extract_first()
        subtypes = response.xpath('//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="类型:"]/following-sibling::text()[1]').extract_first()
        area = response.xpath(u'//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="国家/地区:"]/following-sibling::text()[1]').extract_first()
        alias = response.xpath(u'//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="又名:"]/following-sibling::text()[1]').extract_first()
        summary = response.xpath(u'//article[@class="article-content"]/p[@class="jianjie"]/span/text()').extract_first()
        genres = response.xpath('//header[@class="article-header"]/div[@class="breadcrumbs"]/a[2]/@href').extract_first()
        year = response.xpath('//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="上映日期:"]/following-sibling::text()[1]').re_first(r'\d+')
        imdb = response.xpath(u'//article[@class="article-content"]/div[@class="video_box"]/div[@class="video_info"]/strong[text()="IMDb编码:"]/following-sibling::text()[1]').extract_first()

        mItem['imgs'] = imgs.strip() if imgs else ''
        mItem['title'] = title.strip('《').strip('》') if title else ''
        mItem['year'] = year if year else time.localtime(time.time()).tm_year
        mItem['directors'] = directors.strip().split(' / ') if directors else []
        mItem['actors'] = actors.strip().split(' / ') if actors else []
        mItem['subtypes'] = subtypes.strip().split(' / ') if subtypes else []
        mItem['area'] = area.strip().split(' / ') if area else []
        mItem['alias'] = alias.strip().split(' / ') if alias else []
        mItem['summary'] = summary.strip() if summary else ''
        mItem['slname'] = '91mjw'
        mItem['slcode'] = response.url.split('/')[-1]
        mItem['slink'] = response.url
        mItem['imdb'] = imdb.strip() if imdb else ''
        mItem['genres'] = self.genres[genres.strip().split('/')[-1]] if genres else 1

        eplinkstext = response.xpath(u'//article[@class="article-content"]/div[@class="video_list_li"]/div[@class="vlink"]/a/text()').extract()
        eplinks = response.xpath(u'//article[@class="article-content"]/div[@class="video_list_li"]/div[@class="vlink"]/a/@id').extract()

        if len(eplinks) == 0:
            eplinkstext = response.xpath(u'//article[@class="article-content"]/div[@class="mplay"]/div[@class="mplay-list"]/a/text()').extract()
            eplinks = response.xpath(u'//article[@class="article-content"]/div[@class="mplay"]/div[@class="mplay-list"]/a/@href').extract()

        diceplink = []
        for idx in range(len(eplinks)):
            diceplink.append((eplinkstext[idx].replace('线路',''), eplinks[idx]))
        
        # 解析eplinks url
        mItem['eplinks'] = []
        epno = 0
        for key, arg in diceplink:
            epno = epno + 1
            if arg.startswith('?Play='):
                vidurl = response.url + arg
            elif arg.startswith('/vplay/'):
                vidurl = 'https://91mjw.com{0}'.format(arg)
            else:
                vidurl = 'https://91mjw.com/vplay/{0}.html'.format(arg)
            vid = self.get_links(vidurl)
            # print(vidurl, vid)
            playurl = vid['vid']
            playtype = vid['play_type']
            if playtype == 'mc' or playtype == 'mcs' or playtype == 'mp':
                playurl = 'userID=&type=mc&vkey={0}'.format(playurl)
            elif vid['play_type'] == 'p2p':
                playurl = unquote(playurl)
            mItem['eplinks'].append({
                'epno' : epno,
                'title' : key,
                'playurl' : playurl,
                'args': arg,
                'playgate': 'vlt_' + vid['play_type']
            })
        mItem['dbid'] = ''
        return mItem 
    
    def get_links(self, link):
        splash_script='''
        function main(splash, args)
            splash:autoload([[
                function get_vide(){ return {vid, play_type}; }
            ]])
            assert(splash:go(args.url))
            return splash:evaljs("get_vide()")
        end
        '''
        response = requests.post('http://0.0.0.0:8050/execute?url='+link+'&lua_source='+quote(splash_script), headers={'Content-Type': 'application/javascript'})
        return json.loads(response.text)