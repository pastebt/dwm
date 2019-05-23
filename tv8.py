# -*- coding: utf8 -*-

from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1


class TV8(DWM):
    handle_list = ['/tv8\.fun/', '.dayi.ca/']

    def query_info(self, url):
        url = 'http://www.dayi.ca/ys/?p=2386&page=52'
        hutf = self.get_hutf(url)
        #echo(hutf)
        ct = SelStr("div#content-outer div#content", hutf)[0]
        title = ct.select('h3')[0].text
        p = ct.select('p')[0]
        title = title + '_' + p.text.split()[0]
        echo(title)
        u = match1(p.text, 'video:(\S+)')
        u = u.strip('"').strip("'")
        echo(u)
        us = self.try_m3u8(u)
        return title, None, us, None

    def get_playlist(self, url):
        #url = 'http://tv8.fun/20170328-人民的名义/'
        hutf = self.get_hutf(url)
        #echo(hutf)
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
        #echo(self.get_playlist('http://tv8.fun/20170328-人民的名义/'))
        url = 'http://www.dayi.ca/ys/?p=2386&page=52'
        

if __name__ == '__main__':
    start(TV8)
