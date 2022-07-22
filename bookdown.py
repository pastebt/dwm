# -*- coding: utf8 -*-

import re
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1


class BOOKDN(DWM):
    handle_list = ['bookdown.com.cn']

    def query_info(self, url):
        # http://m.bookdown.com.cn/read/31314_97_2.html
        hutf = self.get_hutf(url)
        echo(hutf)
        us = self._get_m3u8_urls(url, hutf)
        #return "", "mp4", us, None
        return "", None, us, None

    def test1(self, args):
        # http://m.bookdown.com.cn/read/31314.html
        url = 'http://m.bookdown.com.cn/read/31314.html'
        #hutf = self.get_hutf(url)
        #print hutf
        #m = re.findall("http://m.bookdown.com.cn/read/31314_\d+.html", hutf)
        #print m
        #hutf = self.get_html("http://m.bookdown.com.cn/read/31314_2.html")
        #print(hutf)
        #url = "http://m.bookdown.com.cn/read/31314_1.html"
        #url = "http://m.bookdown.com.cn/read/31314_1_2.html"
        while True:
            print >> sys.stderr, url
            hutf = self.get_hutf(url)
            # class="articlecon
            for div in SelStr('div.articlecon', hutf):
                #echo(div)
                #echo(" ".join(div.text.split("&nbsp;")))
                echo(re.sub(u"分节阅读.+，请点击下一页继续阅读。", "",
                     re.sub("&nbsp;", " ", div.text)))
            #echo(hutf)
            m = re.findall(u'''<a class="btn" href="(http://m\.bookdown\.com\.cn/read/31314_.+\.html)">下一章</a>''', hutf)
            #m = re.findall(u'''\<a class="btn" href=".+"\>下一章\</a\>''', hutf) #, re.U)
            #echo(m)
            if not m:
                break
            url = m[0]
            #break

    def test(self, args):
        url = "http://www.bookdown.com.cn/bookinfo/30258.html"
        #url = "http://www.bookdown.com.cn/read/30258_1.html"
        ret = match1(url, "/bookinfo/(\d+)\.html", "/read/(\d+).*\.html")
        bid = int(ret[0])
        echo("bid =", bid)
        url = "http://www.bookdown.com.cn/read/%d_1.html" % bid
        while True:
            #print >> sys.stderr, url
            hutf = self.get_hutf(url)
            #echo(hutf)
            for div in SelStr('div#view_content_txt', hutf):
                echo(re.sub(u"分节阅读.+，请点击下一页继续阅读。", "",
                     re.sub("&nbsp;", " ", div.text)))
            al = SelStr("a#nextPage", hutf)
            if not al:
                break
            url = al[0]['href']
            #break
        

if __name__ == '__main__':
    start(BOOKDN)
