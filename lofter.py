# -*- coding: utf8 -*-

import re
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1


class LOFTER(DWM):
    handle_list = ['lofter.com']

    def query_info(self, url):
        # http://m.bookdown.com.cn/read/31314_97_2.html
        hutf = self.get_hutf(url)
        echo(hutf)
        us = self._get_m3u8_urls(url, hutf)
        #return "", "mp4", us, None
        return "", None, us, None

    def get_list(self, url, name):
        #hutf = self.chrome_hutf(url)
        #echo(hutf)
        hutf = open("l.html").read()
        hutf = hutf.decode("utf8", 'ignore')
        ret = []
        for li in SelStr("ul.list.ctag-0", hutf):
            #echo(len(li))
            echo("======== " + li.text)
            for a in li("a"):
                for h in a("h3"):
                    #if "诸神黄昏" in str(h):
                    if name in h.text:
                        #ret.append(a)
                        # FIXME change host
                        url = "http://leobarack.lofter.com" + a['href']
                        if url not in ret:
                            ret.append(url)
                            echo(url)
                        break
        return ret

    def download(self, url, name):
        for u in self.get_list(url, name):
            self.download_one(u)

    def download_one(self, url):
        hutf = self.get_hutf(url)
        data = SelStr("div.main div.content div.text", hutf)[0]
        t = data("h2 a")[0]
        title = t.text
        echo(title)
        fout = open(title + ".txt", "a")
        fout.write(data.text.encode("utf8"))
        fout.close()

    def test(self, args):
        url = "http://leobarack.lofter.com/post/1e2466b9_1c67d177f"

    def test1(self, args):
        url = "http://leobarack.lofter.com/view"
        #hutf = self.chrome_hutf(url)
        #echo(hutf)
        hutf = open("l.html").read()
        #hutf = hutf.decode("utf8", 'ignore')
        ret = []
        for li in SelStr("ul.list.ctag-0", hutf):
            #echo(len(li))
            #echo("======== " + li.text)
            for a in li("a"):
                for h in a("h3"):
                    if "诸神黄昏" in str(h):
                        ret.append(a)
                        #echo(str(a))
                        echo(a['href'])
                        break
        

if __name__ == '__main__':
    #start(LOFTER)
    if len(sys.argv) != 3:
        echo("Usage: " + sys.argv[0] + " --one url")
        echo("Usage: " + sys.argv[0] + " url name")
        sys.exit(1)
    if sys.argv[1] == "--one":
        LOFTER().download_one(sys.argv[2])
    else:
        LOFTER().download(sys.argv[1], sys.argv[2].decode("utf8"))
