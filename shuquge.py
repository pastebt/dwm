# -*- coding: utf8 -*-

import os
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1


class SHUQUGE(DWM):
    handle_list = ['shuquge.com']

    def query_info(self, url):
        #url = "https://www.shuquge.com/txt/12236/46252712.html"
        hutf = self.get_hutf(url)
        #echo(hutf)
        ct = SelStr("div.content", hutf)
        #echo(ct.text)
        t = SelStr("div.content h1", hutf)[0]
        #return "", "mp4", us, None
        return t.text, "epub", ct, 1

    def save_book(self, outfn, ct):
        #echo(outfn)
        with open(outfn, "w") as fout:
            dat = unicode(ct[0])
            fout.write(dat.encode('utf8'))

    def get_playlist(self, url):
        #url = "https://www.shuquge.com/txt/12236/index.html"
        base = os.path.dirname(url)
        hutf = self.get_hutf(url)
        #hutf = open("s.html").read().decode('utf8')
        #echo(hutf)
        tt = SelStr("div.book div.info h2", hutf)
        if not tt:
            return []
        #echo(tt[0].text)
        title = tt[0].text
        echo(title)
        ul = SelStr("div.listmain dl", hutf)
        if not ul:
            return []
        #for u in ul.descendants:
        sel = True
        lst = []
        for u in ul[0].children:
            #echo(u)
            if u.tag == 'dt':
                sel =  u"最新章节" not in u.text
                continue

            if sel and u.tag == 'dd':
                l = os.path.join(base, u.select("a")[0]['href'])
                echo(l, u.text)
                lst.append((u.text, l))
        return lst

    def test(self, args):
        url = "https://www.shuquge.com/txt/12236/46252712.html"
        hutf = open("s1.html").read().decode('utf8')
        #hutf = self.get_hutf(url)
        #echo(hutf)
        #ct = SelStr("div.content", hutf)[0]
        echo(ct.text)
    

if __name__ == '__main__':
    start(SHUQUGE)
