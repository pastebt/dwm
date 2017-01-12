# -*- coding: utf8 -*-

import os
import re
import sys
from subprocess import Popen, PIPE

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

from comm import DWM, echo, start, debug


class DRAMA8(DWM):
    handle_list = ['/8drama.com/']

    def query_info(self, url):
        #./phantomjs htl.js 300 http://8drama.com/122804/
        #http://8drama.net/ipobar_.php?sign=251438194e51429438981c908a9a1da179242edc4e51&id=gq$$UEN3a0tGazJSeTAyTURROUtEbEdSVkE3TmpGTk95ZEpNaXhFU1RRMlJFRklQQ1UxSnpoUVlHQUtZQW89$$drama&type=html5
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        m = re.search("""\<source src="(http\://8drama\."""
                      """(net/ipobar_|com/ggpic)"""
                      """\.php[^<> ]+)" type""", hutf)
        url = m.group(1)
        url = HTMLParser().unescape(url)
        debug("query_info, url = " + url)
        m = re.search("<title>([^<>]+)</title>", hutf)
        title = m.groups()[0]
        title = title.split("|")[0].strip()
        title = self.align_title_num(title)
        k, size = self.get_total_size([url])
        t = k.split("/")[1]
        self.check_exists(title, t)
        return title, t, [url], size

    def get_playlist(self, page_url):
        hutf = self.get_hutf(page_url)
        m = re.findall('<td width="20%"><a href="(http://8drama.com/\d+/)">([^<>]+)<',
                      hutf)
        if self.align_num == 0:
            self.align_num = len(str(len(m)))
        return [(t, u) for u, t in m]


if __name__ == '__main__':
    start(DRAMA8)
