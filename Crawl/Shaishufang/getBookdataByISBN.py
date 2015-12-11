# -*- coding:utf-8 -*-
import unirest, json, time, socket
from collections import OrderedDict
from multiprocessing import Pool

def PutData(isbnurls):
    """ data """
    spidername = 'ShaishufangAmazon'
    cnt = 0
    for url in isbnurls:
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
        if ((cnt%300)==0):
            time.sleep(3)


if __name__ == '__main__':
    baseurl = 'http://192.168.100.3:5001/book?isbn='
    isbnurls = []
    with file('./shaishufang.isbns.txt', 'rb') as fi:
        for line in fi.readlines():
            isbnurls.append(baseurl + line.strip())
    fi.close()

    PutData(isbnurls[49304:])

    """
    testurl = isbnurls[:10]

    t1 = time.time()
    pool = Pool()
    pool.map(PutData, testurl)
    pool.close()
    pool.join()
    t2 = time.time()
    print (t1-t2)
    """
