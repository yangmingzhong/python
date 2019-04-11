#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#author mz 1306643459
__author__ = 'mingzhong'
from urllib import request,error,parse 
import time
import re
import random
import requests
from bs4 import BeautifulSoup
import mysql.connector
from multiprocessing import Pool
haha56host = 'http://www.haha56.net/'
def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content.decode('utf-8')
    
#存储数据库
def insertContentDATA(insertData):

    conn = mysql.connector.connect(host='127.0.0.1',user='root', password='', database='testpython')
    cursor = conn.cursor()
# 插入一行记录，注意MySQL的占位符是%s:
    #cursor.execute('insert into szs_contents (title, content) values (%s, %s)', insertData)     
    #一次插入多条
    cursor.executemany('insert into szs_contents (title, content) values (%s, %s)', insertData)     
    conn.commit()
    cursor.close()    
def getLoadData(urlA = '/main/fqxh/',frontPage = 1):
    req = request.Request(haha56host+urlA);
    UrlPar = parse.urlparse(urlA)
    nowTail = UrlPar.path.split('/')[-1]
    #该网站做了一些不规则链接，我们需要另外解析
    if nowTail.find('.html'):
        nowFront = urlA.replace(nowTail,'')
    else :
        nowFront = urlA;
    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36",
        "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)"
    ]    
    #这个网站做了一点限制，模拟游览器头部
    req.add_header('User-Agent',random.choice(USER_AGENTS))
    #读取整个网页
    
    # html = requests.get('http://www.haha56.net/main/fqxh/', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}, proxies={"http": "http://{}".format(proxy)})
    #print(html)
    #exit()
    # 使用代理访问   具体代理池 请看 https://github.com/jhao104/proxy_pool  可是我很惆怅，没有几个可以用的。。有好用的免费请悄悄告诉我，感谢
    #proxy = get_proxy()
    #proxy_handler = request.ProxyHandler({'http':  "http://{}".format(proxy)})
    #proxy_auth_handler = request.ProxyBasicAuthHandler()
    #opener = request.build_opener(proxy_handler, proxy_auth_handler)
    #header={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}
    #requestabc = request.Request('http://www.haha56.net/main/fqxh/',headers=header)
    #with opener.open(requestabc) as f:
       # print(f.read())
      #  exit()
    try:
        with request.urlopen(req) as f:
             data = f.read();             
             soup = BeautifulSoup(data,"html.parser",from_encoding="UTF-8")
             #print("标题  \n" + "内容"+'\n'+'链接')
             #用beautifulSoup让读取更简单的  类似jq
             List = []
             #获取当前页面 。我们要做多进程，需要自动走下一个列表
             #有可能捕获空集造成错误 跳过进入下一读取
             if not soup.find('ul',class_='pagelist'):
                 nextPage = int(frontPage)+1; 
                 strRe = re.compile(r'\_\d\.')
                 finaTail = strRe.sub('_'+str(nextPage)+'.',nowTail)
                 nextUrl = nowFront+ finaTail 
                 time.sleep(2)
                 getLoadData(nextUrl,nextPage)
                 exit()
             
             page = soup.find('ul',class_='pagelist').find('li',class_='thisclass').get_text()
             
             if not page:
                 page = frontPage

             #当前页面我们每次需要进程，下一个进程需要要递增这个数据
             nextUrl = ''
         
             for ulTag in soup.find('ul',class_='pagelist').find_all('li'):
                 nextPage = int(page)+1; 
                 textTag =  ulTag.get_text()
                 if not textTag.isdigit():
                      textTag = 0
                 if int(textTag) == nextPage:
                     hrefNextUrl = ulTag.find('a').get('href')
                     #如果不存在子集拼接
                     #网站做下一页链接需要列表需要最后一页显示，我们自己切割链接
                     if not hrefNextUrl:
                         strRe = re.compile(r'\_\d\.')
                         finaTail = strRe.sub('_'+nextPage+'.',nowTail)
                         nextUrl = nowFront+ finaTail 
                     else :
                         nextUrl = nowFront+hrefNextUrl                    
                     break
             delhostRes = re.compile(r'http://([a-z0-9\-._~%]+)')
             for tag in soup.find_all('dl'):
                 geturl  = tag.find('a').get('href');
                 url = delhostRes.sub('',geturl)        
                 #剔除域名
                 #发现这里的内容不符合我们的需求。我们需要完整内容，斗智斗勇的时候到了,各个网站捉取方式不同，包括今天可用，不代表明天可以用
                 #title = tag.find('a').get_text();
                 #content = tag.find('dd',class_='preview').get_text();
                 #print(title+"\n" + content+'\n'+url)
                 #进入子页面
                 childReq = request.Request(haha56host+url);
                 childReq.add_header('User-Agent',random.choice(USER_AGENTS))
                 with request.urlopen(childReq) as cf:
                      childData = cf.read();
                       
                      childSoup = BeautifulSoup(childData,"html.parser",from_encoding="GBK")
                      childTitle = childSoup.find('div',class_='title').get_text();
                      parentSoup = childSoup.find('div',class_='content');
                      List.append([childTitle,parentSoup.get_text()])
                      #观察多次发现数据不存在同一性，该网站是富文本框直接编辑,不存在共性
                   #   for childTag in parentSoup.find_all('p'):
                    #      childP = [childTitle,childTag];
                     #     print(childP)
                        #  List.append(childP)

             #存储入数据库,一个页面数据采集完在存入数据库
             insertContentDATA(List); 
             #每个页面采集完延迟一会递归下一个页面,防止被墙
             time.sleep(4)
             print('当前采集页面'+urlA+'，页码'+page)
             #获取下一个，页面
             getLoadData(nextUrl,page);
             #递归调用下一个页面             
    except error.HTTPError as reason:
        print('采集结束')     
if __name__ == '__main__' :        
    getLoadData('/xiaohua/list6_1.html')
    #这边是 多进程
    #p = Pool(4)
    #for i in range(1,5):
     #   p.apply_async(getLoadData,args=('/main/fqxh/list_21_'+str(i)+'.html',))
    #p.close()
    #p.join()

                       
        
