import requests
import re
from urllib.parse import urlparse
import time
import os
import random
import webbrowser as web
from urllib import parse
import json

username = ''
password = ''

# 登录


def login(username, password):
    url = 'https://passport.weibo.cn/sso/login'
    data = {
        'username': username,
        'password': password
    }
    headers = {
        'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'MIX 2S_9_weibo_9.7.3_android'
    }
    session = requests.Session()
    response = session.post(url, data=data, headers=headers)
    print("登录响应结果:", response)
    try:
        respJson = response.json()
        if("retcode" in respJson):
            if (respJson['retcode'] != 20000000):
                return ""
        else:
            return ""
    except:
        return ""
    cookie = requests.utils.dict_from_cookiejar(session.cookies)
    cookieStr = ""
    for key, value in cookie.items():
        cookieStr = cookieStr + key + "=" + value + ";"
    return cookieStr

# 获取超话列表


def getChaohuaList(cookie, sinceId):
    #url = "https://m.weibo.cn/api/container/getIndex?containerid=100803_-_followsuper"
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100803_-_page_my_follow_super"
    #url = "https://m.weibo.cn/api/container/getIndex?containerid=100803_-_followsuper&sudaref=login.sina.com.cn"
    if sinceId != '':
        url = url + "&since_id=%s" % sinceId
    # print(url)
    headers = {
        'Cookie': cookie,
        'User-Agent': 'MIX 2S_9_weibo_9.7.3_android',
        # 'referer': 'https://m.weibo.cn/p/tabbar?containerid=100803_-_recentvisit&page_type=tabbar'
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    try:
        respJson = response.json()
    except:
        return ""
    return respJson

# 解析超话数据


def resolveChaohua(cardGroup):
    # print(cardGroup)
    chaohuaList = []
    for card in cardGroup:
        if card['card_type'] == "8":
            #print(card['itemid'], ":", card['title_sub'])
            scheme = card['scheme']
            query = urlparse(scheme).query
            parmsList = query.split('&')
            containerid = ''
            for parm in parmsList:
                r = parm.split('=')
                if r[0] == 'containerid':
                    containerid = r[1]
                    break
            chaohua = {
                'title_sub': card['title_sub'],
                'containerid': containerid
            }
            chaohuaList.append(chaohua)
    return chaohuaList

# 超话签到


def signin(cookie, item):
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    data = {
        'ajwvr': 6,
        'api': 'http://i.huati.weibo.com/aj/super/checkin',
        'texta': '签到',
        'textb': '已签到',
        'status': 0,
        'id': item['containerid'],
        'location': 'page_%s_super_index' % item['containerid'][0:6],
        'timezone': 'GMT 0800',
        'lang': 'zh-cn',
        'plat': 'Win32',
        'screen': '1920*1080',
        'ua': ua,
        '__rnd': int(round(time.time() * 1000))
    }
    url = "https://weibo.com/p/aj/general/button"
    headers = {
        'Cookie': cookie,
        'User-Agent': ua,
        'Referer': 'https://weibo.com/p/%s/super_index' % item['containerid'],
        'X-Forwarded-For': '62.144.102.168',
        'CLIENT-IP': '62.144.102.168'
    }
    session = requests.Session()
    response = session.get(url, headers=headers, params=data)
    respJson = response.json()
    # print(respJson)
    if 'code' in respJson:
        if respJson['code'] == '100000':
            print("超级话题->%s签到成功!" % item['title_sub'])
            print(respJson['data']['alert_title'])
            print("接口返回码:%s" % respJson['code'])
            print("接口返回描述:%s" % respJson['msg'])
        else:
            print("超级话题->%s签到失败!" % item['title_sub'])
            print("接口返回码:%s" % respJson['code'])
            print("接口返回描述:%s" % respJson['msg'])
            if respJson['code'] == '100003':
                print("微博检测到行为异常，将打开页面%s进行验证......" %
                      respJson['data']['location'])
                web.open_new(respJson['data']['location'])
                time.sleep(10)
                print("尝试重新签到......")
                signin(cookie, item)
    else:
        print("%s签到失败!" % item['title_sub'])
        print("没有返回码（♯▼皿▼）")


if __name__ == '__main__':
    # 读取文件的cookie值，若不存在则进行登录操作
    file = open('weibocookie', 'r+')
    tempCookie = ""
    try:
        tempCookie = file.read()
    finally:
        file.close
    if tempCookie == '':
        print("cookies为空，将重新登录获取cookies")
        tempCookie = login(username, password)
        if tempCookie == '':
            print("登录失败!")
            input()
        # 将重新获取的cookie保存到文件中
        with open('weibocookie', 'w') as f:
            f.write(tempCookie)
            f.close
    # 获取超话列表
    chaohuaList = []
    sinceId = ""
    isBreak = True
    lastFollow = ""
    while isBreak:
        #print("sinceId:", sinceId)
        respJson = getChaohuaList(tempCookie, sinceId)
        cardlistInfo = respJson['data']['cardlistInfo']
        cardGroupParent = respJson['data']['cards'][0]
        if cardGroupParent['card_type_name'] != 'follow_super_follow':
            cardGroupParent = respJson['data']['cards'][1]
        cardGroup = cardGroupParent['card_group']
        chaohuaList = chaohuaList + resolveChaohua(cardGroup)
        if 'since_id' in cardlistInfo:
            sinceId = cardlistInfo['since_id']
            if sinceId == '':
                print("获取超级话题列表结束...准备开始签到")
                break
            if json.loads(sinceId)['follow'] == lastFollow:
                print("获取超级话题列表结束...准备开始签到")
                break
            else:
                lastFollow = json.loads(sinceId)['follow']
    # 循环遍历 进行签到
    print("总共要签到的超级话题数为:", len(chaohuaList))
    count = 0
    for item in chaohuaList:
        print("-------------------")
        print("准备签到超级话题->%s" % item['title_sub'])
        signin(tempCookie, item)
        print("-------------------")
        #time.sleep(random.randint(1, 5))
        count = count + 1
