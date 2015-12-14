# -*- coding:utf-8 -*-
import unirest, json, time
from collections import OrderedDict

def PutData(isbnurls):
    """ data """
    spidername = 'ShaishufangAmazon'
    cnt = 0
    for url in isbnurls:
        #print cnt, '-->', url
        cnt += 1
        unirest.timeout(180)
        response = unirest.get(url, headers={"Accept":"application/json"}) # handle url = baseurl + isbn
        try:
            #bookdt
            bookdt = response.body['isbn']
            bookdt['spider'] = spidername
            #data style
            datadict = {}
            datadict['datas'] = [bookdt]
            #put datadict
            unirest.timeout(180)
            resdata = unirest.put(
                            "http://192.168.100.3:5000/data",
                            headers={ "Accept": "application/json", "Content-Type": "application/json" },
                            params=json.dumps(datadict)
                         )
        except:
            pass
        if ((cnt%80)==0):
            time.sleep(3)

if __name__ == '__main__':
    baseurl = 'http://192.168.100.3:5001/book?isbn='    # server
    #baseurl = 'http://192.168.31.187:5001/book?isbn='   # home-703
    #baseurl = 'http://192.168.1.48:5001/book?isbn='      # kids-5G
    isbnurls = []
    with file('./shaishufang.isbns.txt', 'rb') as fi:
        for line in fi.readlines():
            isbnurls.append(baseurl + line.strip())
    fi.close()

    #105601 
    PutData(isbnurls[99601:-6000])
