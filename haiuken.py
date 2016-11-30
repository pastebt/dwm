#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
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
        ips = [r['src'].split("://")[1].split('/')[0] for r in ret]
        echo(ips)
        #return

        urls = []
        total_size = 0
        for u, s in ret:
            urls.append(u)
            total_size += int(s)
        if urls:
            k, s = get_kind_size(urls[0])
            k = k.split('/')[-1]
        else:
            k = ''
        #echo(k)
        #return
        return title, k, urls, total_size


#class MyHTMLParser(HTMLParser):
#    def __init__(self):
#        HTMLParser.__init__(self)
#        self.step = 
#
#    def handle_starttag(self, tag, attrs):



if __name__ == '__main__':
    start(HYG)
    #a = "aHR0cDovLzUwLjk3Ljk0LjYyL2hhaXVrZW5jb20vaG90L0I2Mkg1Lm1wND9zdD05UWVVbjd4cTViTFUyWldkbG1xZGxnJmU9MTQ4MDQ2ODczMA=="
    #echo(base64.b64decode(a))
