#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
#from subprocess import Popen, PIPE
#from html.parser import HTMLParser

from comm import DWM, match1, echo, start, get_kind_size


class DYB(DWM):     #dianyingbar
    def __init__(self):
        DWM.__init__(self)
        self.extra_headers = {'Referer': "http://bodekuai.duapp.com/ckplayer/ckplayer.swf"}

    def query_info(self, url):
        # get flv part list
        html = self.get_html(url)
        hutf = html.decode('utf8')
        ret = re.findall("<video><file><\!\[CDATA\[([^<>]+)\]\]></file>"
                         "<size>(\d+)</size>"
                         "<seconds>\d+</seconds></video>",
                         hutf)
        #print(ret)
        urls = []
        total_size = 0
        for u, s in ret:
            urls.append(u)
            total_size += int(s)
        if urls:
            k, s = get_kind_size(urls[0])
            k = k.split('/')[-1]
        else:
            k = ''
        #echo(k)
        #return
        return None, k, urls, total_size

    def try_playlist(self, ispl, url):
        # http://www.dianyingbar.com/9111.html
        # http://www.dianyingbar.com/3970.html
        # get xml
        html = self.get_html(url)
        hutf = html.decode('utf8')
        ret = re.findall("videoarr.push\('YKYun\.php\?id\=([^\(\)]+)'\)", hutf)
        #print(ret[0])
        t = self.title
        #pl = ["http://bodekuai.duapp.com/api/yUrl.php?id=" + r for r in ret]
        pl = []
        for i, r in enumerate(ret, start=1):
            pl.append(("%s_%02d" % (t, i),
                       "http://bodekuai.duapp.com/api/yUrl.php?id=" + r))
        echo(pl)
        return pl


if __name__ == '__main__':
    start(DYB)
