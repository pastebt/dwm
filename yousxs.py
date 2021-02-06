# -*- coding: utf8 -*-

import re
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1, norm_url


class DRAMA8(DWM):
    handle_list = ['(/|\.)yousxs\.com(/|:)']

    def query_info(self, url):
        # http://8drama.com/122804/
        #http://8drama.net/ipobar_.php?sign=251438...
        hutf = self.get_hutf(url)
        url = SelStr('video source', hutf)[0]['src']
        title = SelStr('h1.entry-title', hutf)[0].text
        return title, None, [url], None

    def get_playlist(self, url):
        ns = SelStr('div.entry-content.rich-content tr td a',
                    self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]

    def test(self, argv):
        #url = "https://www.yousxs.com/4659.html"
        url = "https://www.yousxs.com/player/4659_1.html"
        #hutf = self.get_hutf(url)
        #echo(hutf)
        hutf = open("y_4659_1.html").read().decode("utf8")
        #skey = match1(hutf, " var\S+skey\s*=\s*'(\S+)'\s*;")
        skey = match1(hutf, "\s+var\s+skey\s*=\s*'(\S+)'\s*;")
        echo(skey)
        mp3url = match1(hutf, " '(\S+skey=)'\s*\+\s*skey")
        #echo(quote(mp3url.encode('utf8'), ":?=/"))
        echo(norm_url(mp3url + skey)) #.encode('utf8')))


if __name__ == '__main__':
    start(DRAMA8)
