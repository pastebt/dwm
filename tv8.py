# -*- coding: utf8 -*-

import json

from mybs import SelStr, DataNode
from comm import DWM, echo, start, match1


class TV8(DWM):
    handle_list = ['/tv8\.fun/', '.dayi.ca/']

    def query_info(self, url):
        hutf = self.get_hutf(url)
        #obj = match1(hutf, r" var\s+videoObject\s*\=\s*({[^}]+})")
        #mu = match1(obj, ' video:\s*(\S+)').strip('"')
        #mu = self.last_m3u8(mu)
        h = SelStr("h3", hutf)[0]
        d = SelStr("div.post-entry p", hutf)[0]
        mu = match1(d.text, ' video:\s*(\S+)').strip('"')
        mu = self.last_m3u8(mu)
        d.children = [c for c in d.children if isinstance(c, DataNode)]
        title = h.text.strip() + " " + d.text.strip()
        return title, "m3u8", mu, None

    def query_info1(self, url):
        # url = 'http://www.dayi.ca/ys/?p=2386&page=52'
        hutf = self.get_hutf(url)
        # echo(hutf)
        ct = SelStr("div#content-outer div#content", hutf)[0]
        title = ct.select('h3')[0].text
        p = ct.select('p')[0]
        title = title + '_' + p.text.split()[0]
        echo(title)
        #echo(p.text)
        u = match1(p.text, 'video:(\S+)')
        #u = u.strip('"').strip("'")
        if u[0] in ("'", '"'):
            u = u.split(u[0])[1]
        echo(u)
        #us = self.try_m3u8(u)
        #return title, None, us, None
        return title, "m3u8", u, None

    def get_playlist(self, url):
        # url = 'http://tv8.fun/20170328-人民的名义/'
        hutf = self.get_hutf(url)
        # echo(hutf)
        img = SelStr("div.entry-content p img", hutf)
        if img:
            title = img[0]['alt']
        else:
            title = SelStr("title", hutf)[0].text
        echo(title)
        us = []
        for p in SelStr("div.entry-content p", hutf):
            n = p.select("strong")
            if n and "M3U" in n[0].text:
                us = [(title + '_' + a.text, a['href']) for a in p.select("a")]
                echo(us)
                break
        return us

    def test(self, argv):
        # try_m3u8
        # echo(self.get_playlist('http://tv8.fun/20170328-人民的名义/'))
        # 'http://www.dayi.ca/ys/?p=3004&page=2'
        #url = 'http://www.dayi.ca/ys/?p=2386&page=52'
        #url = 'http://www.dayi.ca/ys/?p=3004&page=1'
        url = 'http://www.dayi.ca/ys/?p=4076&&page=1'
        hutf = self.get_hutf(url)
        h = SelStr("h3", hutf)[0]
        echo(h.text)
        d = SelStr("div.post-entry p", hutf)[0]
        d.children = [c for c in d.children if isinstance(c, DataNode)]
        echo(d.text)
        #dat = match1(hutf, r" var\s+videoObject\s*\=\s*({[^}]+})")
        #hutf = '''//advertisements:'website:http://dayi.ca/ys/wp-content/themes/responsive-child/ad.json',
        #        video:"https://videos6.jsyunbf.com/20190630/MnyGwQRx/index.m3u8"
                
        #}'''
        #dat = match1(hutf, ' video:\s*(\S+)')
        #dat = dat.strip('"')
        #dat = json.loads(dat)["video"]
        #echo(dat)


if __name__ == '__main__':
    start(TV8)
