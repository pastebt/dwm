#! /usr/bin/python
# -*- coding: utf8 -*-

import re

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


if __name__ == '__main__':
    start(BILIBILI)
