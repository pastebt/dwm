# -*- coding: utf8 -*-

import os
import re
import sys

from mybs import SelStr
from comm import DWM, match1, echo, start, debug, py3, get_kind_size


class TTWanDa(DWM):     # http://www.ttwanda.com/
    handle_list = ['\.ttwanda\.com/films/', '\.ttwanda\.com/tv/']

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
        if t and '/films/' in url:
            title = t
        src = SelStr('iframe.player', hutf)[0]['src']

        if '/player/v.php?url=' in src:
            # http://www.ttwanda.com/tv/ustv/945.html
            # ../../player/v.php?url=www.le.com/ptv/vplay/20723618.html
            src = 'http://' + src.split('?url=', 1)[1]
            from letv import LETV
            return LETV().query_info(src)

        if not src.startswith("http://") and not src.startswith("https://"):
            src = 'http://www.ttwanda.com/' + src
        echo(src)
        self.extra_headers['Referer'] = url     # this is important
        hutf = self.get_hutf(src)
        dst = match1(hutf, 'var play_url \= "([^"]+)"')
        echo(dst)
        if not dst:
            echo("Can not find var play_url")
            sys.exit(1)
        if ('youku.com/' in dst and '/m3u8' in dst) \
            or 'lecloud.com/' in dst \
            or '/letv-uts/' in dst:
            return title, None, self.try_m3u8(dst), None
        if 'ttwanda.com/ftn_handler/' in dst:
            cs = ["%s=%s" % (c.name, c.value) for c in self.cookie.cookiejar if c.name != 'PHPSESSID']
            echo(cs)
            self.wget_cookie = "; ".join(cs)
            k, s = get_kind_size(dst, self.wget_cookie)
            return title, k, [dst], s
        #if 'mgtv.com/' in dst or '189.cn/v5/downloadFile' in dst:
        #    # http://www.ttwanda.com/films/us/907.html?style=cq
        #    return title, None, [dst], None
        #echo('TTWanda has new source')
        #echo(dst)
        #sys.exit(1)
        return title, None, [dst], None

    def try_m3u8(self, src):
        #url = 'http://www.ttwanda.com/films/us/2091.html?ac'
        # http://www.ttwanda.com/films/us/1881.html?le  mp2t
        urls = []
        for line in self.get_html(src).split('\n'):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
        return urls

    def get_playlist(self, url):
        if not '/tv/' in url:
            return []
        url = url.split('?')[0]
        hutf = self.get_hutf(url)
        ns = SelStr('div.article-paging a', hutf)
        # href="?vid=20723618&amp;title=第01集 新局长崛起"
        urls = []
        for a in ns:
            vid = match1(a['href'], 'vid=(\d+)')
            if vid:
                urls.append((a.text, url + '?vid=' + vid))
            else:
                urls.append((a.text, url + a['href']))
        return urls

    def test(self, args):
        # /tv/ustv/945.html?vid=20723618&title=第01集%20新局长崛起
        url = 'http://www.ttwanda.com/tv/ustv/945.html'
        url = 'http://www.ttwanda.com/tv/ustv/945.html?vid=20723618&title=%E7%AC%AC01%E9%9B%86%20%E6%96%B0%E5%B1%80%E9%95%BF%E5%B4%9B%E8%B5%B7'
        html = self.get_hutf(url)


if __name__ == '__main__':
    start(TTWanDa)
