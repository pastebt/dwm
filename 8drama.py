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
from comm import DWM, echo, start, debug


class DRAMA8(DWM):
    def query_info(self, url):
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #echo(html)
        #m = re.search("\<source\s* src=\"(http://8drama.net/ipobar_.php[^<> ]+)\"\s* type", hutf)
        #if not m:
        #    m = re.search("\<source\s* src=\"(http://8drama.com/ggpic.php[^<> ]+)\"\s* type", hutf)
        #    if not m:
        #        echo(html)
        #        return None
        m = re.search("""\<source src="(http\://8drama\."""
                      """(net/ipobar_|com/ggpic)"""
                      """\.php[^<> ]+)" type""", hutf)
        if not m:
            echo(html)
            return None
        url = m.group(1)
        url = HTMLParser().unescape(url)
        debug("query_info, url = " + url)
        m = re.search("<title>([^<>]+)</title>", hutf)
        title = m.groups()[0]
        title = title.split("|")[0].strip()
        title = self.align_title_num(title)
        #title = '_'.join(title.split('/'))
        k, size = self.get_total_size([url])
        t = k.split("/")[1]
        self.check_exists(title, t)
        return title, t, [url], size

    def download_urls(self, title, ext, urls, totalsize):
        outfn = os.path.join(self.out_dir, title + "." + ext)
        echo("download", outfn)
        dwnfn = outfn + ".dwm"
        #return
        #p = Popen(["wget", "-nv", "--show-progress", "-O", outfn, urls[0]])
        #p = Popen(["wget", "-O", outfn, urls[0]])
        p = Popen(["wget", "-c", "-O", dwnfn, urls[0]])
        #p = Popen(["wget", "-O", dwnfn, urls[0]])
        p.wait()
        if os.stat(dwnfn).st_size == totalsize:
            os.rename(dwnfn, outfn)

    def get_list(self, page_url):
        html = self.get_html(page_url)
        hutf = html.decode('utf8')
        m = re.findall("""<td width="20%"><a href="(http://8drama.com/\d+/)">([^<>]+)<""",
                      hutf)
        self.align_num = len(str(len(m)))
        for u, t in m:
            yield t, u
        #echo(m.groups())
        #print m
        #yield ""


if __name__ == '__main__':
    start(DRAMA8)
