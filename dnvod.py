# -*- coding: utf8 -*-

import os
import re
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, debug, get_kind_size


class DNVOD(DWM):     # http://dnvod.eu/
    handle_list = ['dnvod']

    def query_info(self, url):
        #url = 'https://www.dnvod.eu/Movie/Readyplay.aspx?id=deYM01Pf0bo%3d'
        hutf = self.get_hutf(url)
        #echo(hutf)
        title = SelStr('span#bfy_title >', hutf)[0].data.strip()
        debug('title =', title)
        for script in SelStr('script', hutf):
            txt = script.text
            if 'PlayerConfig' not in txt:
                continue
            vid = match1(txt, "id: '([^']+)',")
            key = match1(txt, "key: '([^']+)',")
            break
        debug('vid =', vid)
        debug('key =', key)
        u = "https://www.dnvod.eu/Movie/GetResource.ashx?id=%s&type=htm" % vid
        self.extra_headers['Referer'] = url
        durl = self.get_html(u, postdata="key=" + key)
        debug(durl)

        k, tsize = get_kind_size(durl)
        k = k.split('/')[-1]
        return title, k, [durl], tsize

    def get_playlist(self, url):
        #url = 'https://www.dnvod.eu/Movie/detail.aspx?id=NU%2bOQHwQObI%3d'
        #url = 'https://www.dnvod.eu/Movie/Readyplay.aspx?id=deYM01Pf0bo%3d'
        hutf = self.get_hutf(url)
        urls = []
        for a in SelStr('ul[data-identity=guest] > li > div.bfan-n > a', hutf):
            debug(a.text, a['href'])
            urls.append((a.text, 'https://www.dnvod.eu' + a['href']))
        return urls


if __name__ == '__main__':
    start(DNVOD)
