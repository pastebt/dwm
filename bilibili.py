#! /usr/bin/python
# -*- coding: utf8 -*-

import re
import sys

from comm import DWM, echo, start, debug


class BILIBILI(DWM):
    appkey = '8e9fc618fbd41e28'

    def query_info(self, url):
        html = self.get_html(url)
        hutf = html.decode('utf8')
        m = re.search('''<div class="v-title"><h1 title="([^<>]+)"''', hutf)
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
        ms = re.findall('<durl>\s+<order>\d+</order>\s+'
                       '<length>\d+</length>\s+<size>(\d+)</size>\s+'
                       '<url><\!\[CDATA\[([^<>]+)]]></url>', html, re.M)
        ext = ms[0][1].split('?')[0][-3:]
        totalsize = 0
        urls = []
        for s, u in ms:
            totalsize += int(s)
            urls.append(u)
        #print total
        #print urls
        #print ext
        return title, ext, urls, totalsize

    def try_playlist(self, ispl, url):
        # http://www.bilibili.com/video/av4197196/
        m = re.match("(https?://[^/]+)/(video/av\d+)", url)
        if !m:
            raise Exception("Unsupport bilibili")
        h, i = m.group(1), m.group(2)
        print h, i
        sys.exit(0)
        html = self.get_html(url)
        hutf = html.decode('utf8')
        pl = re.findall("<option value='(/%s/index_\d+.html)'>([^<>]+)</option>" , hutf)


if __name__ == '__main__':
    start(BILIBILI)
