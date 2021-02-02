# -*- coding: utf8 -*-

import re
import json
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from mybs import SelStr, DataNode
from comm import DWM, echo, start, match1, U, debug


class TV8(DWM):
    no_check_certificate = True
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
        title = h.text.strip() + "_" + d.text.strip()
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
        hutf = self.get_hutf(url)
        #m = re.search(U("通用版.+第(\d+)集"), p[3].text)
        #if m:
        #    max_id = int(m.group(1))
        #else:
        #    m = re.search(U("首播:.+共(\d+)集"), p[0].text) #, flags=re.M+re.U)
        #    max_id = int(m.group(1))
        t = SelStr("h1.entry-title", hutf)[0]
        m = re.search(U("(.+) 至第(\d+)集"), t.text)
        title, max_id = m.group(1).strip(), int(m.group(2))

        p = SelStr("div.entry-content p", hutf)
        for a in p[1].select("a"):
            uo = urlparse.urlparse(a['href'])
            qs = urlparse.parse_qs(uo.query)
            if 'p' in qs and 'page' in qs:
                pn = int(qs['p'][0])
                break
        us = [(U("%s_第%02d集") % (title, i), "http://www.dayi.ca/ys/?p=%d&page=%d" % (pn, i)) for i in range(1, max_id + 1)]
        debug(us)
        return us

    def get_playlist1(self, url):
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
        #url = 'http://www.dayi.ca/ys/?p=4076&&page=1'
        url = 'http://tv8.fun/%e4%b8%8a%e9%98%b3%e8%b5%8b/' # 上阳赋
        hutf = self.get_hutf(url)
        #echo(hutf)
        t = SelStr("h1.entry-title", hutf)[0]
        m = re.search(U("(.+) 至第(\d+)集"), t.text)
        echo(m.group(1), m.group(2))
        p = SelStr("div.entry-content p", hutf)
        echo(p[3].text)
        m = re.search(u"通用版.+第(\d+)集", p[3].text)
        echo(m.group(1))
        m = re.search(U("首播:.+共(\d+)集"), p[0].text) #, flags=re.M+re.U)
        echo(m.group(1))
        for a in p[1].select("a"):
            if 'page=' not in a['href']:
                continue
            uo = urlparse.urlparse(a['href'])
            qs = urlparse.parse_qs(uo.query)
            echo(qs)
            break


if __name__ == '__main__':
    start(TV8)
