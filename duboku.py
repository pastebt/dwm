# -*- coding: utf8 -*-

import json

from mybs import SelStr
from comm import DWM, echo, start, match1


class DUBOKU(DWM):
    handle_list = ['/duboku\.co/', '/www.duboku\.co/']

    def query_info(self, url):
        hutf = self.get_hutf(url)
        dat = match1(hutf, r"var\s+player_data\s*\=\s*({[^}]+})")
        mu = self.last_m3u8(json.loads(dat)['url'])
        #us = self.try_m3u8(u)
        t = SelStr("h2.title", hutf)[0]
        title = '_'.join(t.text.split())
        return title, "m3u8", mu, None
        #echo(us)

    def get_playlist(self, url):
        hutf = self.get_hutf(url)
        t = SelStr("h2.title a", hutf)[0]
        t = t.text.strip()
        ns = SelStr('div#playlist1 a', hutf)
        return [(t + "_" + a.text.strip(), "https://www.duboku.co" + a['href']) for a in ns]

    def test(self, argv):
        url = "https://www.duboku.co/vodplay/1433-1-1.html"
        hutf = self.get_hutf(url)
        dat = match1(hutf, r"var\s+player_data\s*\=\s*({[^}]+})")
        dat = json.loads(dat)
        echo(dat['url'])
        #us = self.try_m3u8(dat['url'])
        #echo(us)
        t = SelStr("h2.title", hutf)[0]
        echo(' '.join(t.text.split()))

        
if __name__ == '__main__':
    start(DUBOKU)
