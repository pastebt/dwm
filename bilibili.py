#! /usr/bin/python
# -*- coding: utf8 -*-

import re
import sys

from comm import DWM, echo, start, debug, search_first


class BILIBILI(DWM):
    appkey = '8e9fc618fbd41e28'

    def query_info(self, url):
        h, p = self.get_h_p(url)
        html = self.get_html(url)
        hutf = html.decode('utf8')
        #m = re.search("<option value='/%s/index_\d+.html' selected>"
        #              "([^<>]+)</option>" % p, hutf)
        #if not m:
        #    m = re.search("<option value='/%s/index_\d+.html'>"
        #                  "([^<>]+)</option>" % p, hutf)
        #    if not m:
        #        m = re.search('<div class="v-title"><h1 title="([^<>]+)"',
        #                       hutf)
        m = search_first(hutf,
                         "<option value='/%s/index_\d+.html' selected>"
                         "([^<>]+)</option>" % p,
                         "<option value='/%s/index_\d+.html'>"
                         "([^<>]+)</option>" % p,
                         '<div class="v-title"><h1 title="([^<>]+)"')
        title = m.group(1)
        title = self.align_title_num(title)
        #echo(title.encode('utf8'))
        echo(title)
        #return
        m = re.search('''cid=(\d+)&''', hutf)
        cid = m.group(1)
        echo("cid =", cid)

        html = self.get_html('http://interface.bilibili.com/playurl?appkey=' +
                             self.appkey + '&cid=' + cid)
        #echo(html)
        hutf = html.decode('utf8')
        ms = re.findall('<durl>\s+<order>\d+</order>\s+'
                       '<length>\d+</length>\s+<size>(\d+)</size>\s+'
                       '<url><\!\[CDATA\[([^<>]+)]]></url>', hutf, re.M)
        ext = ms[0][1].split('?')[0][-3:]
        totalsize = 0
        urls = []
        for s, u in ms:
            totalsize += int(s)
            urls.append(u)
        return title, ext, urls, totalsize

    def get_h_p(self, url):
        # http://www.bilibili.com/video/av4197196/
        m = re.match("(https?://[^/]+)/(video/av\d+)", url)
        if not m:
            raise Exception("Unsupport bilibili url format")
        return m.group(1), m.group(2)

    def try_playlist(self, ispl, url):
        h, p = self.get_h_p(url)
        #print h, p
        html = self.get_html(url)
        hutf = html.decode('utf8')
        m = re.search("<option value='(/%s/index_\d+.html)' selected>"
                      "([^<>]+)</option>" % p, hutf)
        if m:
            pl = [(m.group(1), m.group(2))]
        else:
            pl = re.findall("<option value='(/%s/index_\d+.html)'>"
                            "([^<>]+)</option>" % p, hutf)
        #print pl
        return [(self.align_title_num(t), h + u) for u, t in pl]
        #sys.exit(0)


if __name__ == '__main__':
    start(BILIBILI)
