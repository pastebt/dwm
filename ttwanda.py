# -*- coding: utf8 -*-

import os
import re
import sys

from mybs import SelStr
from comm import DWM, match1, echo, start, debug, py3, get_kind_size


class TTWanDa(DWM):     # http://www.ttwanda.com/
    handle_list = ['ttwanda\.com/films/']

    def query_info(self, url):
        #url = 'http://www.ttwanda.com/films/us/1693.html?xf'
        hutf = self.get_hutf(url)
        if not '?' in url:
            a = SelStr('section.p5 div a', hutf)[0]['href']
            url = url + a
            hutf = self.get_hutf(url)
        title = SelStr("div.video-content article p strong", hutf)[0].text
        r = "《(.+)》"
        if not py3:
            r = r.decode('utf8')
        t = match1(title, r)
        if t:
            title = t
        #echo(title)
        src = 'http://www.ttwanda.com' + SelStr('iframe.player', hutf)[0]['src']
        echo(src)
        self.extra_headers['Referer'] = url     # this is important
        hutf = self.get_hutf(src)
        #echo(hutf)
        dst = match1(hutf, 'var play_url \= "([^"]+)"')
        echo(dst)
        if not dst:
            echo("Can not find var play_url")
            sys.exit(1)
        if 'youku.com/partner/m3u8' in dst or 'lecloud.com/' in dst:
            return title, None, self.try_m3u8(dst), None
        if 'ttwanda.com/ftn_handler/' in dst:
            cs = {}
            for c in self.cookie.cookiejar:
                if c.name == 'PHPSESSID':
                    continue
                cs[c.name] = c.value
            echo(cs)
            self.wget_cookie = cs
            k, s = get_kind_size(dst, cs)
            return title, k, [dst], s
        echo('TTWanda has new source')
        echo(dst)
        sys.exit(1)

    def try_m3u8(self, src):
        #url = 'http://www.ttwanda.com/films/us/2091.html?ac'
        urls = []
        for line in self.get_html(src).split('\n'):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
        return urls


if __name__ == '__main__':
    #start(TTWanDa)
    TTWanDa().query_info(1)
