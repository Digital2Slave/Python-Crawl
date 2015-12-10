##Get Amazon Book ASIN by ISBN

1. Use **urllib2.urlopen** with random user-agent.

2. User crawlera proxy with userkey.

3. get sel, page, status, url from **1.** and **2.** with the help of scrapy.Selector.

4. analysis the url page by xpath language.


###Notethat
* I use key by local user by edit the ***.bash_profile*** in user home dir, like:

```
    #in .bash_profile
    export CRAWLERAKEY=<KEY>
    #out .bash_profile
    source .bash_profile
```

* Get the **CRAWLERAKEY** by use **os** module in python language, like:

```
    import os
    userkey = os.environ.get("CRAWLERAKEY")
```

* Now you know it. By the way, **CRAWLERAKEY** is not free!
