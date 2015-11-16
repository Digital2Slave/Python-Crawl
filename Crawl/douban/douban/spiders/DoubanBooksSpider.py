#!/usr/local/bin/python
#-*- encoding:utf-8 -*-

import scrapy, re, urlparse, cPickle
from scrapy import Request
from scrapy.spiders import CrawlSpider, Spider,Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor as sle

from douban.items import DoubanbooksItem
#http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/
# 001411031239400f7181f65f33a4623bc42276a605debf6000
from collections import OrderedDict

#scrapy crawl doubanSpider -s JOBDIR=crawls/doubanSpider -s MONGODB_DB=douban -s MONGODB_COLLECTION=book

class DoubanBooksSpider(Spider):

    name = "doubanSpider"
    allowed_domains = ["douban.com"]
    start_urls = ["http://book.douban.com/tag/?view=type"]

    '''
    #!< 禁用重定向 '403':禁止访问,对 Internet 服务管理器 的访问仅限于 Localhost.
    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, meta = {'dont_redirect': True,'handle_httpstatus_list': [403]})
    '''

    #!< 获取子分类下的URLS
    def parse(self, response):

        sel   = Selector(text=response.body)
        #文学:0~26    [27]  27
        #流行:27~62   [36]  63
        #文化:63~95   [33]  96
        #生活:96~116  [21]  117
        #经管:117~129 [13]  130
        #科技:130~114 [15]  115
        sites = sel.xpath('//a[@class="tag"]/@href').extract()
        for site in sites:
            site = site.replace('?focus=','')
            yield Request(site, callback=self.PagesParse)

    #!< 从子类'第一页'开始处理每一页，获取每一页中每本书的链接
    def PagesParse(self, response):

        sel = Selector(text=response.body)
        bookinfo = sel.xpath('//div[@class="mod book-list"]/dl/dd')
        # 单本书的url
        if bookinfo:
            # 处理下一页
            nextpage = sel.xpath('//span[@class="next"]/a/@href').extract()
            np = nextpage[0]
            np = response.urljoin(np)
            yield Request(np, callback=self.PagesParse)

        # 单本书的url
        if bookinfo:
            # process every book information (bi) TYPE: scrapy.selector.unified.Selector
            for bi in bookinfo:
                # bookurl and rate TYPE: list
                bookurl = bi.xpath('a/@href').extract()
                rate    = bi.xpath('div/span[@class="rating_nums"]/text()').extract()
                if (bookurl != []):
                    burl = bookurl[0]
                    if rate:
                        x = float(rate[0])
                        if (x>=8.5) and (x<9.0): # 书籍评分
                            yield Request(burl, callback=self.BookParse)

    #!< 单独处理每一本书籍信息
    def BookParse(self, response):

        item = DoubanbooksItem()
        sel = Selector(text=response.body)

        # OrderedDict的Key会按照插入的顺序排列
        orderdict = OrderedDict()

        #!< 书名，书籍封面URL，评分
        title  = sel.xpath('//div[@id="wrapper"]/h1/span/text()').extract()
        if (title !=[]):
            orderdict[u'书名'] = title[0]
        else:
            orderdict[u'书名'] = ''

        coverurlTmp = sel.xpath('//div[@id="mainpic"]/a/img/@src').extract()
        coverurl = str()
        if (coverurlTmp != []):
            coverurlv = coverurlTmp[0]
            if ('mpic' in coverurlv):
                coverurl = coverurlv.replace('mpic','lpic')
        orderdict[u'书籍封面'] = coverurl

        rateTmp = sel.xpath('//div[@class="rating_wrap"]/p/strong/text()').extract()
        rate = str()
        if (rateTmp != []):
            rate = rateTmp[0].strip()
        orderdict[u'评分'] = rate


        #!< 作者，出版社，原书名，译者，出版年，页数，定价，装帧，丛书，ISBN
        sels = sel.xpath('//div[@id="info"]/span')

        for tree in sels:

            tv = tree.xpath('text()').extract()
            tv = tv[0].strip(':') if (tv!=[]) else ('') # title value

            # 作者，译者
            tvs = tree.xpath('span/text()').extract()
            tvs = tvs[0].strip() if (tvs!=[]) else ('')
            if (tvs != ''):
                tv = tvs

            # 其他
            afind = str()
            afind = tree.xpath('following-sibling::text()').extract_first().strip()

            if (afind == ''):
                # 作者，译者
                av = tree.xpath('a/text()').extract()
                av = av[0].strip() if (av!=[]) else ('') # <a> text </a>
                if (av == ''):
                    # 丛书
                    avs = sel.xpath('//div[@id="info"]/a/text()').extract()
                    avs = avs[0].strip() if (avs!=[]) else ('')
                    afind = avs
                else:
                    afind = av
            orderdict[tv] = afind


        #!< 内容简介 & 作者简介
        titles = sel.xpath('//div[@class="related_info"]/h2')
        values = sel.xpath('//div[@class="related_info"]/div')

        if (values != []):

            lenth = len(titles) if (len(titles)<=len(values)) else len(values)
            flag = True if (values[0].xpath('div[@class="ebook-promotion"]')) else False

            if flag:
                for i in xrange(lenth):

                    title = titles[i]
                    t = title.xpath('span/text()').extract()
                    t = t[0] if (t!=[]) else ('')

                    content = str()
                    if (values[i].xpath('div[@class="ebook-promotion"]')):

                        contenttmp = values[i+1].xpath('span[@class="all hidden"]/div/div[@class="intro"]/p/text()').extract()
                        if contenttmp:
                            content = contenttmp
                        else:
                            content = values[i+1].xpath('div/div[@class="intro"]/p/text()').extract()
                    else:
                        contenttmp = values[i+1].xpath('span[@class="all hidden"]/div/div[@class="intro"]/p/text()').extract()
                        if contenttmp:
                            content = contenttmp
                        else:
                            content = values[i+1].xpath('div/div[@class="intro"]/p/text()').extract()

                    if (i<2):
                        orderdict[t] = content
            else:
                for i in xrange(lenth):

                    title = titles[i]
                    t = title.xpath('span/text()').extract()
                    t = t[0] if (t!=[]) else ('')

                    content = str()
                    contenttmp = values[i].xpath('span[@class="all hidden"]/div/div[@class="intro"]/p/text()').extract()
                    if contenttmp:
                        content = contenttmp
                    else:
                        content = values[i].xpath('div/div[@class="intro"]/p/text()').extract()
                    orderdict[t] = content

        #!< 标签
        tags = sel.xpath('//div[@class="indent"]/span/a/text()').extract()
        tags = tags if (tags != []) else ('')
        orderdict[u'标签'] = tags

        #!< 相关推荐书目
        recom = sel.xpath('//div[@class="content clearfix"]/dl/dt/a/@href').extract()
        if (recom != []):
            subjectid = [ s[s.find('subject/')+8:-1] for s in recom if ('ebook' not in s)]
            orderdict[u'相关推荐书目'] = subjectid
        else:
            orderdict[u'相关推荐书目'] = ''

        #!< 书籍购买来源
        buybook = sel.xpath('//ul[@class="bs noline more-after "]/li/a/@href').extract()
        buybook = buybook if (buybook != []) else ('')
        orderdict[u'书籍购买来源'] = buybook

        #!< 书籍链接
        orderdict[u'书籍链接'] = response.url

        item['bookinfo'] = orderdict

        yield item
