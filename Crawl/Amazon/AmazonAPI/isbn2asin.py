#-*- encoding:utf-8 -*-
import requests
import random, os, json
from scrapy import Selector
from urllib2 import urlopen,Request
from requests.auth import HTTPProxyAuth
import sys, time
sys.setrecursionlimit(250)


#http://www.useragentstring.com/pages/useragentstring.php
browerfile = file('./UserAgentString.json', 'rb')
browerdata = json.load(browerfile)
browerfile.close()

PCbrower = browerdata['brower']      #9502
MBbrower = browerdata['mobilebrower']#512
user_agent_list = PCbrower+MBbrower

def getSelPagebyUrlProxy(url):
    """ get url's sel, page, url, request status by proxy."""
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
    """ get url's sel, page, url, request status."""
    request_headers = { 'User-Agent': random.choice(user_agent_list) }
    request = Request(url, None, request_headers)
    if (request!=None):
        req = urlopen(request, timeout=60)
        page = req.read()
        status = req.getcode()
        sel = Selector(text=page)
        return sel, page, url, status
    else:
        time.sleep(1)
        return getSelPagebyUrl(url)


def getASIN(isbn):
    url = 'http://www.amazon.cn/s/ref=nb_sb_noss?field-keywords=' + isbn
    sel, page, url, status = getSelPagebyUrl(url)

    nores = sel.xpath('//h1[@id="noResultsTitle"]/text()').extract()
    if nores:
        #print nores[0] #没有找到任何与
        return ''
    else:
        res = sel.xpath('//li[@id="result_0"]/@data-asin').extract()
        if res:
            return res[0]
        else:
            time.sleep(1)
            return getASIN(isbn)


def test(isbn):
    if (isbn!='') and (type(isbn)==str):
        asin = getASIN(isbn)
        print '%s-->%s' % (isbn, asin)

if (__name__=='__main__'):
    # Test done.
    isbn = '9787561335321'
    test(isbn)
