#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
import json
try:
    import urllib.parse as urllib
except ImportError:
    import urllib

import base64

from comm import DWM, match1, echo, start, get_kind_size
from mybs import MyHtmlParser, select


class HYG(DWM):     #http://haiuken.com/ 海宇根
    def query_info(self, url):
        # http://haiuken.com/theatre/2muu/
        html = self.get_html(url)
        #echo(html)
        hutf = html.decode('utf8', 'ignore')
        m = MyHtmlParser(tidy=False)
        m.feed(hutf)
        title = m.select("head title")[0].text
        if title.startswith("Theatre - "):
            title = title[10:]
        echo(title)

        ret = m.select(".bg2 .tmpl img")
        ips = json.dumps([r['src'].split("://")[1].split('/')[0] for r in ret])
        echo(ips)
        #return

        d = {"xEvent": "UIMovieComments.Error",
             "xJson": ips}
        html = self.get_html("http://haiuken.com/ajax/theatre/2muu/",
                             data=urllib.urlencode(d).encode("utf8"))
        ret = json.loads(html.decode('utf8'))
        url = base64.b64decode(ret['Data']['Error'].encode('utf8'))
        #echo(url)

        urls = [url.decode('utf8')]
        echo(urls)
        #return
        total_size = 0
        #for u, s in ret:
        #    urls.append(u)
        #    total_size += int(s)
        #if urls:
        k, total_size = get_kind_size(urls[0])
        k = k.split('/')[-1]
        #echo(k)
        #echo(total_size)
        #return
        return title, k, urls, total_size


#class MyHTMLParser(HTMLParser):
#    def __init__(self):
#        HTMLParser.__init__(self)
#        self.step = 
#
#    def handle_starttag(self, tag, attrs):



if __name__ == '__main__':
    print(urllib.unquote("%5B%2250.97.94.62%22%2C%22173.193.195.182%22%5D"))
    start(HYG)
    #a = "aHR0cDovLzUwLjk3Ljk0LjYyL2hhaXVrZW5jb20vaG90L0I2Mkg1Lm1wND9zdD05UWVVbjd4cTViTFUyWldkbG1xZGxnJmU9MTQ4MDQ2ODczMA=="
    #echo(base64.b64decode(a))
