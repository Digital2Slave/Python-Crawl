#!/usr/local/bin/python
#-*- encoding:utf-8 -*-
from urllib2 import urlopen,Request
from scrapy import Selector
import requests, json
import random, socket, os
import unirest
from requests.auth import HTTPProxyAuth

#http://www.useragentstring.com/pages/useragentstring.php
browerfile = file('./UserAgentString.json', 'rb')
browerdata = json.load(browerfile)
browerfile.close()

PCbrower = browerdata['brower']      #9502
MBbrower = browerdata['mobilebrower']#512
user_agent_list = PCbrower+MBbrower

def getSelPagebyUrl(url):

    request_headers = { 'User-Agent': random.choice(user_agent_list) }
    request = Request(url, None, request_headers)
    req = urlopen(request, timeout=60)
    page = req.read()
    status = req.getcode()
    sel = Selector(text=page)
    return sel, page, url, status

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


def getASIN(isbn):

    url = 'http://www.amazon.cn/s/ref=nb_sb_noss?field-keywords=' + isbn
    sel, page, url, status = getSelPagebyUrl(url)
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
