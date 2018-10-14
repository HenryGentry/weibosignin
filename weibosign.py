import requests
import re
from urllib.parse import urlparse
import time
import os

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
        'Content-Type': 'application/x-www-form-urlencoded'
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
    url = "https://m.weibo.cn/api/container/getIndex?containerid=100803_-_page_my_follow_super"
    if sinceId != '':
        url = url + "&since_id=%s" % sinceId
    headers = {
        'Cookie': cookie
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    respJson = response.json()
    return respJson

# 解析超话数据


def resolveChaohua(cardGroup):
    chaohuaList = []
    for card in cardGroup:
        if card['card_type'] == 8:
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
    url = "https://weibo.com/p/aj/general/button?api=http://i.huati.weibo.com/aj/super/checkin&id=%s" % item['containerid']
    headers = {
        'Cookie': cookie
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    respJson = response.json()
    if 'code' in respJson:
        if respJson['code'] == '100000':
            print("%s签到成功!" % item['title_sub'])
            print("返回码为%s" % respJson['code'])
        else:
            print("%s签到失败!" % item['title_sub'])
            print("返回码为%s" % respJson['code'])
    else:
        print("%s签到失败!" % item['title_sub'])
        print("没有返回码（♯▼皿▼）")


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
    if tempCookie=='':
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
while isBreak:
    respJson = getChaohuaList(tempCookie, sinceId)
    cardlistInfo = respJson['data']['cardlistInfo']
    cardGroup = respJson['data']['cards'][0]['card_group']
    chaohuaList = chaohuaList + resolveChaohua(cardGroup)
    if 'since_id' in cardlistInfo:
        sinceId = cardlistInfo['since_id']
    else:
        print("获取超级话题列表结束...准备开始签到")
        break
# 循环遍历 进行签到
for item in chaohuaList:
    print("-------------------")
    print("准备签到%s" % item['title_sub'])
    signin(tempCookie, item)
    print("-------------------")
    time.sleep(1)
