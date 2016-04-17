#!/usr/bin/env python
# -*- coding: utf8 -*-


#./phantomjs htl.js 300 http://8drama.com/122804/
#http://8drama.net/ipobar_.php?sign=251438194e51429438981c908a9a1da179242edc4e51&id=gq$$UEN3a0tGazJSeTAyTURROUtEbEdSVkE3TmpGTk95ZEpNaXhFU1RRMlJFRklQQ1UxSnpoUVlHQUtZQW89$$drama&type=html5

import os
import re
import sys
from subprocess import Popen, PIPE

try:
    from HTMLParser import HTMLParser
    p3 = False
except ImportError:
    from html.parser import HTMLParser
    p3 = True

#import comm
from comm import DWM, echo, start


class DRAMA8(DWM):
    def query_info(self, url):
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #echo(html)
        m = re.search("\<source\s* src=\"(http://8drama.net/ipobar_.php[^<> ]+)\"\s* type", hutf)
        if not m:
            return None
        url = m.groups()[0]
        url = HTMLParser().unescape(url)
        #print url
        m = re.search("<title>([^<>]+)</title>", hutf)
        title = m.groups()[0]
        title = title.split("|")[0].strip()
        k, size = self.get_total_size([url])
        #print title, k, [url], size
        t = k.split("/")[1]
        return title, t, [url], size
        #raise self.ExistsError()

    def download_urls(self, title, ext, urls, totalsize, dstdir):
        outfn = os.path.join(dstdir, title + "." + ext)
        if os.path.exists(outfn):
            echo(outfn, "exists")
            return
        echo("download", outfn)
        #return
        p = Popen(["wget", "-O", outfn, urls[0]])
        p.wait()
        

    def get_list(self, page_url):
        html = self.get_html(page_url)
        hutf = html.decode('utf8')
        m = re.findall("""<td width="20%"><a href="(http://8drama.com/\d+/)">([^<>]+)<""",
                      hutf)
        for u, t in m:
            yield t, u
        #echo(m.groups())
        #print m
        #yield ""


if __name__ == '__main__':
    start(DRAMA8)
