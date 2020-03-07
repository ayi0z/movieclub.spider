# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
import hashlib
import re
import pymongo
import time
import ssl

# 使用 mysql.connector 保存数据到 mysql
class MYSQLPipeline(object):

    def __init__(self, mysql_host, mysql_user, mysql_passwd, mysql_database):
        self.mysql_host = mysql_host
        self.mysql_user = mysql_user
        self.mysql_passwd = mysql_passwd
        self.mysql_database = mysql_database
        print('=============================================================')
        print('-------------------------------------------------------------')
        print('===> start spider > save data in mysql')
        print('===> mysql host: %s' %mysql_host)
        print('===> mysql usr: %s' %mysql_user)
        print('===> mysql db: %s' %mysql_database)
        print('-------------------------------------------------------------')
        print('=============================================================')

    @classmethod
    def from_crawler(cls, crawler):
        # 价值 settings
        return cls(
            mysql_host = crawler.settings.get('MYSQL_HOST'),
            mysql_user = crawler.settings.get('MYSQL_USER'),
            mysql_passwd = crawler.settings.get('MYSQL_PASSWD'),
            mysql_database = crawler.settings.get('MYSQL_DATABASE')
        )

    def open_spider(self, spider):
        self.db = mysql.connector.connect(
            host = self.mysql_host,
            user = self.mysql_user,
            passwd = self.mysql_passwd,
            database = self.mysql_database,
            auth_plugin = 'mysql_native_password'
        )
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()

    def process_item(self, item, spider):
        print(item)
        # 检查 item 是否已经保存过
        slname = item['slname'] 
        slcode = item['slcode']
        self.cursor.execute('SELECT uid,tpid FROM m_sourlnk WHERE name = %s and lnk_code = %s', (slname, slcode))
        slnkid_tpid = self.cursor.fetchone()
        if slnkid_tpid :
            # 更新eplnks
            self.update_eplnks(slnkid_tpid, item)
        else:
            # 插入新电影
            self.insert_new_item(item)
        return item

    # 更新eplnks： 先删除旧的eplnks， 在插入新的eplnks
    def update_eplnks(self, slnkid_tpid, item):
        slnkid, tpid = slnkid_tpid
        # slnkid = slnkid.decode(encoding='utf-8')
        # tpid = tpid.decode(encoding='utf-8')
        print('===> update eplnks > tpid:%s  slnkid:%s  title:%s' %(tpid, slnkid, item['title']))
        delsql, delval = self._sql_del_eplnk(tpid, slnkid)
        epsql, epval = self._sql_insert_eplnk(tpid, slnkid, item)
        try:
            self.cursor.execute(delsql, delval)
            self.cursor.executemany(epsql, epval)
            self.db.commit()
        except Exception as e:
            print('===================================================')
            print('=====> update_eplnks exception: ', e)
            print('=====> tpid:%s   title:%s    slnkid:%s   dbid:%s' %(tpid, item['title'], slnkid, item['dbid']))
            print('===================================================')
            self.db.rollback()

    # 插入新电影
    def insert_new_item(self, item):
        print('===> insert > title:%s' %item['title'])
        tpid, tpsql, tpval = self._sql_insert_titlepage(item)
        slnkid, slsql, slval = self._sql_insert_sourlnk(tpid, item)
        epsql, epval = self._sql_insert_eplnk(tpid, slnkid, item)

        try:
            self.cursor.execute(tpsql, tpval)
            self.cursor.executemany(slsql, slval)
            self.cursor.executemany(epsql, epval)
            self.db.commit()
        except Exception as e:
            print('===================================================')
            print('=====> insert_new_item exception: ', e)
            print('=====> tpid:%s   title:%s    slnkid:%s   dbid:%s' %(tpid, item['title'], slnkid, item['dbid']))
            print('===================================================')
            self.db.rollback()

    # 构建 insert titlepage sql语句
    def _sql_insert_titlepage(self, item):
        timetick = int(time.time()*1000)
        tpsql = '''INSERT INTO `movieclub`.`m_titlepage`
        (`uid`, `title`, `alias`, `imgs`, `genres`, `directors`, `actors`, `area`, `subtype`, `year`, `summary`, `mocode`, `pubdate`, `latime`, `dbid`, `imdb`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        tpid = hashlib.md5((str(item['year']) + item['title']+item['imgs']+str(item['genres'])).encode('utf-8')).hexdigest()
        tpval = (
            tpid,
            item['title'],
            ','.join(item['alias']),
            item['imgs'],
            item['genres'],
            ','.join(item['directors']),
            ','.join(item['actors']),
            ','.join(item['area']),
            ','.join(item['subtypes']),
            item['year'],
            item['summary'][:8000] if item['summary'] is not None else '',
            str(item['genres']) + tpid[0:9],
            timetick,
            timetick,
            item['dbid'],
            item['imdb']
        )
        return (tpid, tpsql, tpval)

    # 构建 insert sourlnk sql语句
    def _sql_insert_sourlnk(self, tpid, item):
        slnkid = hashlib.md5(item['slink'].encode('utf-8')).hexdigest()
        timetick = int(time.time()*1000)
        slsql = '''INSERT INTO `movieclub`.`m_sourlnk`(`uid`, `tpid`, `name`, `lnk_code`, `lnk_url`, `pubdate`, `latime`) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        slval = [(slnkid, tpid, item['slname'], item['slcode'], item['slink'], timetick, timetick)]
        dbid = item['dbid'].strip().strip("'").strip()
        if dbid and len(dbid) > 4: # 如果有豆瓣id，那么同时insert 豆瓣链接记录
            dbslnkid = hashlib.md5((tpid+dbid).encode('utf-8')).hexdigest()
            slval.append((dbslnkid, tpid, 'douban', dbid, 'https://movie.douban.com/subject/' + dbid + '/'))
        return (slnkid, slsql, slval)

    # 构建 insert eplnk sql语句
    def _sql_insert_eplnk(self, tpid, slnkid, item):
        epsql ='''INSERT INTO `movieclub`.`m_eplnk`(`uid`, `tpid`, `slnkid`, `epno`, `title`, `playurl`, `playgate`, `args`, `pubdate`, `latime`) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)'''
        epval = []
        timetick = int(time.time()*1000)
        for epl in item['eplinks']:
            epid = hashlib.md5((str(epl['epno'])+slnkid+epl['playurl']).encode('utf-8')).hexdigest()
            eptitle = re.sub(r"'|大结局|播放|画面|声音|字幕修复|字幕修正|修正|修复|缺|.mp4|(限免)", '', epl['title'], 0, re.I).strip()
            epval.append((epid, tpid, slnkid, epl['epno'], eptitle.strip(), epl['playurl'], epl['playgate'], epl['args'], timetick, timetick))
        return (epsql, epval)

    # 构建 del eplnk sql语句
    def _sql_del_eplnk(self, tpid, slnkid):
        delsql = 'DELETE FROM m_eplnk WHERE slnkid=%s AND tpid=%s'
        delval = (slnkid, tpid)
        return (delsql, delval)

# 使用 pymongo 保存数据到 mongodb
class PYMONGOPipeline(object):

    mongo_colname = 'mediascover'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        print('-------------------------------------------------------------')
        print('===> start spider > save data in mongo')
        print('===> mongo uri: %s' %mongo_uri)
        print('===> mongo db: %s' %mongo_db)
        print('===> mongo collection: %s' %self.mongo_colname)
        print('-------------------------------------------------------------')
        print('=============================================================')

    @classmethod
    def from_crawler(cls, crawler):
        # 价值 settings
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # isQs = item['subtypes'].find('情色') > -1
        # if isQs :
        #     print('===> skip > title:%s type:%s' %(item['title'],item['subtypes']))
        #     return item
        slink = item['slink'].strip('http://').strip('https://')
        query = { '$or':[{"syncsource": 'http://' + slink}, {"syncsource": 'https://' + slink}] }
        ex_cids = self.db[self.mongo_colname].find(query,{'cid':1})
        if ex_cids.count() > 0:
            for cid in ex_cids :
                # 更新eplnks
                self.update_eplnks(cid['cid'], item)
        else :
            # 插入新电影
            self.insert_new_item(item)
        return item
    
    def insert_new_item(self, item):
        print('===> insert new > %s' %item['title'])

        tpid = hashlib.md5((str(item['year']) + item['title']+item['imgs']+str(item['genres'])).encode('utf-8')).hexdigest()
        timetick = int(time.time()*1000)
        dictitem = {
            "cid":tpid,
            "dbid":item['dbid'].strip().strip("'").strip(),
            "type":item['genres'],
            "title":item['title'].strip(),
            "title_en":"",
            "alias":item['alias'],
            "year":item['year'],
            "area":item['area'][:1] if item['area'] else '',
            "langue":"",
            "director":item['directors'],
            "actor":item['actors'],
            "subtype":item['subtypes'],
            "desc":item['summary'],
            "score":{"douban":"0"},
            "pic":item['imgs'],
            "pubdate":timetick,
            "istrailer":"0",
            "epscount":"0",
            "epsprog":{"isall":"0", "epsc":""},
            "eps":[
                {
                    "epid":hashlib.md5((str(timetick)+str(epl['epno'])+epl['playurl']).encode('utf-8')).hexdigest(),
                    "title":re.sub(r"'|大结局|播放|画面|声音|字幕修复|字幕修正|修正|修复|缺|.mp4|(限免)", '', epl['title'], 0, re.I).strip(),
                    "playgate":epl['playgate'],
                    "url":epl['playurl'],
                    "args":epl['args'],
                    "hot":"0",
                    "isoff":"0"
                } for epl in item['eplinks']
            ],
            "hot":0,
            "mocode":str(item['genres']) + tpid[0:9],
            "isoff":"0",
            "syncsource":item['slink'],
            "latime":timetick,
            "newtoday":item['newtoday']
        }
        self.db[self.mongo_colname].insert_one(dictitem)
    
    def update_eplnks(self, cid, item):
        print('===> update > %s' %(item['title']))

        timetick = int(time.time()*1000)
        query = {'cid': cid}
        val = {'$set': {
            "title":item['title'].strip(),
            "alias":item['alias'],
            "latime":timetick,
            "newtoday":item['newtoday'],
            'eps':[
                {
                    "epid":hashlib.md5((str(timetick)+str(epl['epno'])+epl['playurl']).encode('utf-8')).hexdigest(),
                    "title":re.sub(r"'|大结局|播放|声音|字幕修复|字幕修正|修正|修复|缺|.mp4|(限免)", '', epl['title'], 0, re.I).strip(),
                    "playgate":epl['playgate'],
                    "url":epl['playurl'],
                    "args":epl['args'],
                    "hot":"0",
                    "isoff":"0"
                } for epl in item['eplinks']
            ]
        }}
        self.db[self.mongo_colname].update_one(query, val)