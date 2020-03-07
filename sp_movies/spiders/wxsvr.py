import pymongo
import datetime
import ssl
import requests
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

mongo_uri = 'mongodb+srv://mobox_ayi:okm,lp@mobox-t31ru.azure.mongodb.net/mobox?retryWrites=true'
mongo_db = 'mobox'
mongo_colname = 'mediascover'

def wx_accesstoken():
    # appid = 'wxdd581fcfefdd4b87'
    # appsecret = '061bb2b485777a9bd27d9024993f392e'
    appid = 'wxdd581fcfefdd4b87'
    appsecret = '069ebc55f47d3b50b643f83bbf631de5'
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}'.format(appid, appsecret)
    res = requests.get(url)
    print(res.text)
    access_token = json.loads(res.text)['access_token']
    print('access_token: ', access_token)
    return access_token

def auto_todayupdate():
    return
    print('ready to publish today update titles')
    today = str(datetime.date.today())
    client = pymongo.MongoClient(mongo_uri, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
    db = client[mongo_db]
    newtoday =db[mongo_colname].find({'newtoday':today},{'title':1, 'year':1, 'area':1, 'type':1 }).sort([('type', pymongo.ASCENDING)])
    newtitle = []
    genres = {
        1:'电影',
        2:'剧集',
        3:'动漫',
        4:'综艺'
    }
    for one in newtoday:
        newtitle.append(r'<li><p style=\"font-size:12px;\">{3}.《{0}》 .{1}.{2}<\/p><\/li>'.format(one['title'], one['year'], ' | '.join(one['area']), genres[one['type']]))

    # if len(newtitle) == 0:
    #     print('no update new')
    #     return

    yesterday = str(datetime.date.today() + datetime.timedelta(-1))
    newyesterday = db[mongo_colname].find({'newtoday':yesterday},{'title':1, 'year':1, 'area':1, 'type':1 }).sort([('type', pymongo.ASCENDING)])
    yesternewtitle = []
    for one in newyesterday:
        yesternewtitle.append(r'<li><p style=\"font-size:12px;\">{3}.《{0}》 .{1} .{2}<\/p><\/li>'.format(one['title'], one['year'], ' | '.join(one['area']), genres[one['type']]))
    
    if len(newtitle) == 0 and len(yesternewtitle) == 0:
        print('no update new')
        return
        
    if len(yesternewtitle) > 0:
        yestercontent = r'<ol class=\" list-paddingleft-2\" style=\"list-style-type: decimal;\">{0}<\/ol><br/>'.format(''.join(yesternewtitle))

    content = r'''<p style=\"text-align: center;\"><img class=\"rich_pages\" data-ratio=\"0.4255555555555556\" data-s=\"300,640\" data-src=\"https://mmbiz.qpic.cn/mmbiz_jpg/dKe1WTSiaJo1Fx23PfT2sWDGxPnEopOPJDHaQk3iamCyJkHPQgqnNJqOG502OxAPuRRpdicJkXCbJZ1NsH2w1pm3w/640?wx_fmt=jpeg\" data-type=\"jpeg\" data-w=\"900\" style=\"\"  /></p>
    <br/><ol class=\" list-paddingleft-2\" style=\"list-style-type: decimal;\">{0}<\/ol>
    <hr style=\"border-style: solid;border-width: 1px 0 0;border-color: rgba(0,0,0,0.1);-webkit-transform-origin: 0 0;-webkit-transform: scale(1, 0.5);transform-origin: 0 0;transform: scale(1, 0.5);\">
    {1}
    <p><span style=\"color: rgb(61, 167, 66);\"><strong><img data-src=\"https:\/\/res.wx.qq.com\/mpres\/htmledition\/images\/icon\/common\/emotion_panel\/emoji_wx\/2_06.png\" data-ratio=\"1\" data-w=\"20\" style=\"display:inline-block;width:20px;vertical-align:text-bottom;\"  \/>发送指令“<\/strong><\/span><span style=\"color: rgb(255, 76, 65);\"><strong>886699<\/strong><\/span><span style=\"color: rgb(61, 167, 66);\"><strong>”, 可随时查看最新影视资讯。<\/strong><\/span>
    <br/><br/>
    <p><span style=\"font-size: 12px;color: rgb(178, 178, 178);\">注：本文内容由无人值守机器人自动从网络抓取实时生成。<\/span><\/p><\/p>'''
    
    data = {
        "media_id":'8yAf-A_3ReroZmet56JlyLGvLcOvgKuSVkXTeRnZUao',
        "index":0,
        "articles": {
            "title": '{0} 今日数:{1}'.format(today.replace('-',''), len(newtitle)),
            "thumb_media_id": '8yAf-A_3ReroZmet56JlyKzjhHtj59TYgRCDSojEbAY',
            "author": '',
            "digest": '今日收录/更新数（{0}）。也可以随时发送指令“886699”查看。'.format(len(newtitle)),
            "show_cover_pic": 0,
            "content": content.format(''.join(newtitle), yestercontent),
            "content_source_url": '' # ,
            # "need_open_comment": 1,
            # "only_fans_can_comment": 1
        }
    }

    data = json.dumps(data).encode('latin-1').decode('unicode_escape').encode('utf-8')
    access_token = wx_accesstoken()
    url = 'https://api.weixin.qq.com/cgi-bin/material/update_news?access_token={0}'.format(access_token)
    res = requests.post(url, data=data, headers={"Content-Type": "application/json"})
    print(res.text)

def wx_createmenu():
    access_token = wx_accesstoken()
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={0}'.format(access_token)
    # data = {
    #     'button': [{
    #         'type': 'click',
    #         'name': '今日尝鲜',
    #         'key': 'TODAY_NEW_UPDATE'
    #     }]
    # }
    data = {
        'button': [{
            'type': 'view_limited',
            'name': '今天看啥',
            'media_id': '8yAf-A_3ReroZmet56JlyLGvLcOvgKuSVkXTeRnZUao'
        }]
    }
    data = json.dumps(data).encode('latin-1').decode('unicode_escape').encode('utf-8')
    res = requests.post(url, data=data, headers={"Content-Type": "application/json"})
    print(res.text)

def wx_article_list():
    access_token = wx_accesstoken()
    url = 'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={0}'.format(access_token)
    data = {
        "type":'image',
        "offset":10,
        "count":1
    }
    res = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    # print(res.encoding, res.text.encode(res.encoding).decode('utf-8'))
    print(json.dumps(json.loads(res.text.encode(res.encoding).decode('utf-8')), ensure_ascii=False, indent=4))

# auto_todayupdate()