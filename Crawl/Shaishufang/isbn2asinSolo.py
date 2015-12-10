#!/usr/local/bin/python
#-*- encoding:utf-8 -*-
from urllib2 import urlopen,Request
from scrapy import Selector
import requests, json
import random, socket, os
import unirest
from requests.auth import HTTPProxyAuth

user_agent_list = [\
    'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31',\
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',\
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',\
    \
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',\
    'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',\
    'Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',\
    \
    'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',\
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',\
    'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',\
    \
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201',\
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9a3pre) Gecko/20070330',\
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13; ) Gecko/20101203',\
    \
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',\
    'Opera/9.80 (X11; Linux x86_64; U; fr) Presto/2.9.168 Version/11.50',\
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52',\
    \
    'Mozilla/5.0 (Windows; U; Win 9x 4.90; SG; rv:1.9.2.4) Gecko/20101104 Netscape/9.1.0285',\
    'Mozilla/5.0 (Macintosh; U; PPC Mac OS X Mach-O; en-US; rv:1.8.1.7pre) Gecko/20070815 Firefox/2.0.0.6 Navigator/9.0b3',\
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',\
    \
    'Mozilla/39.0 (Macintosh; Intel Mac OS X 10_10_4),' \
    'AppleWebKit/536.5 (KHTML, like Gecko)', \
    'Chrome/19.0.1084.54 Safari/536.5'
]


def getSelPagebyUrlProxy(url):
    # url = "https://www.amazon.cn"
    headers = {}
    proxy_host = "proxy.crawlera.com"
    crawlerakey = os.environ.get("CRAWLERAKEY")
    proxy_auth = HTTPProxyAuth(crawlerakey, "")
    proxies = {"http": "http://{}:8010/".format(proxy_host)}

    if url.startswith("https:"):
        url = "http://" + url[8:]
        headers["X-Crawlera-Use-HTTPS"] = "1"

    req    = requests.get(url, headers=headers, proxies=proxies, auth=proxy_auth)
    page   = req.text
    status = req.status_code
    sel    = Selector(text=page)

    return sel, page, url, status


def getSelPagebyUrl(url):

    request_headers = { 'User-Agent': random.choice(user_agent_list) }
    request = Request(url, None, request_headers)
    req = urlopen(request, timeout=60)
    page = req.read()
    status = req.getcode()
    sel = Selector(text=page)
    return sel, page, url, status


def getASIN(isbn):

    url = 'http://www.amazon.cn/s/ref=nb_sb_noss?field-keywords=' + isbn
    sel, page, url, status = getSelPagebyUrl(url)
    if (status!=200):
        sel, page, url, status = getSelPagebyUrlProxy(url)
        #print 'proxy...'

    res = sel.xpath('//li[@id="result_0"]/@data-asin').extract()
    if (res != []):
        return res[0]
    else:
        return ''

def test(isbn):
    if (isbn!='') and (type(isbn)==str):
        asin = getASIN(isbn)
        print '%s-->%s' % (isbn, asin)

if (__name__=='__main__'):
    # Test done.
    #isbn = '9787561335321'
    #test(isbn)
    isbns = []
    with file('./shaishufang.isbns.txt', 'rb') as fi:
         for line in fi.readlines():
             isbns.append(line.strip())
    fi.close()
    #print len(isbns), isbns[-1]

    step = 10
    subisbnindexs = [ isbns[i:i+step]  for i in range(50000,len(isbns),step) ]

    #print len(subisbnindexs), subisbnindexs[-1][-1]
    #sumlen = 0
    #for sub in subisbnindexs:
    #	sumlen += len(sub)
    #print sumlen
    #print 'Prepare work done......'

    baseurl = 'http://www.amazon.cn/dp/'
    i = 0
    for sub in subisbnindexs:
    	#!<list--one
    	unvisitedurllist = []
    	#cnt = 0
    	for isbn in sub:
    	    asin = getASIN(isbn)
            if (asin != ''):
	            url = baseurl + asin
	            d = {}
	            d['spider'] = 'ShaishufangAmazon'
	            d['url'] = url
	            d['isbn'] = isbn
	            d['asin'] = asin
	            unvisitedurllist.append(d)
                #cnt += 1
    	    #if (cnt%20==0):
    	    #    time.sleep(2)
        #!<dict--two
        unvisitedurldict = {}
        unvisitedurldict['urls'] = unvisitedurllist
        #!<put--three
        unirest.timeout(180)
        res = unirest.put(
                        "http://192.168.100.3:5000/unvisitedurls",
                        headers={"Accept":"application/json", "Content-Type":"application/json"},
                        params=json.dumps(unvisitedurldict)
                        )
        print 'sub: ',step, '--', i, 'Done!'
        i += 1
        if (i==3):
            break
    print 'Test done for crawlera!'
    #with open('./amazonurl.json', 'wb') as fo:
    #	json.dump(unvisitedurldict, fo)
    #fo.close()
