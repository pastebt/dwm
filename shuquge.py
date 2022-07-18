# -*- coding: utf8 -*-

import os
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1


class SHUQUGE(DWM):
    handle_list = ['shuduge.com']

    def query_info(self, url):
        # http://m.bookdown.com.cn/read/31314_97_2.html
        hutf = self.get_hutf(url)
        echo(hutf)
        us = self._get_m3u8_urls(url, hutf)
        #return "", "mp4", us, None
        return "", None, us, None

    def get_index(self, args):
        url = "https://www.shuquge.com/txt/12236/index.html"
        base = os.path.dirname(url)
        #hutf = self.get_hutf(url)
        hutf = open("s.html").read()
        #echo(hutf)
        tt = SelStr("div.book div.info h2", hutf)
        #echo(tt[0].text)
        title = tt[0].text
        echo(title)
        ul = SelStr("div.listmain dl", hutf)[0]
        #for u in ul.descendants:
        sel = True
        lst = []
        for u in ul.children:
            #echo(u)
            if u.tag == 'dt':
                sel =  u"最新章节" not in u.text.decode("utf8")
                continue

            if sel and u.tag == 'dd':
                echo(os.path.join(base, u.select("a")[0]['href']), u.text)
        #echo(base)

    def test(self, args):
        url = "https://www.shuquge.com/txt/12236/46252712.html"
        hutf = open("s1.html").read()
        #hutf = self.get_hutf(url)
        #echo(hutf)
        ct = SelStr("div.content", hutf)[0]
        echo(ct.text)
    

if __name__ == '__main__':
    start(SHUQUGE)
