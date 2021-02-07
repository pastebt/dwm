# -*- coding: utf8 -*-

import json

from mybs import SelStr
from comm import DWM, echo, start, match1, norm_url


class XIMALAYA(DWM):
    handle_list = ['(/|\.)yousxs\.com(/|:)']

    def query_info(self, url):
        #url = "https://www.yousxs.com/player/4659_1.html"
        hutf = self.get_hutf(url)
        title = SelStr("h3", hutf)[0].text
        skey = match1(hutf, "\s+var\s+skey\s*=\s*'(\S+)'\s*;")
        skey = "1ab7d3b36620467d9bd0ca00e3b13ef3"
        mp3url = match1(hutf, " '(\S+skey=)'\s*\+\s*skey")
        u = norm_url(mp3url + skey)
        return title, "mp3", [u], None

    def get_playlist(self, url):
        mid = match1(url, "yousxs.com/(\d+).html")
        hutf = self.get_hutf(url)
        title = SelStr("h3", hutf)[0].text
        al = SelStr("div.panel-body div.col-xs-3 a", hutf)
        ul = []
        for a in al:
            n = match1(a['href'], "player/" + mid + "_(\d+).html")
            if n is None:
                continue
            n = int(n)
            ul.append((u"%s_有声小说_第%02d集" % (title, n),
                       "https://www.yousxs.com/player/%s_%d.html" % (mid, n)))
        return ul
       
    def test(self, argv):
        url = "https://www.ximalaya.com/youshengshu/22658739/"
        url = "https://www.ximalaya.com/youshengshu/22658739/202502304"
        url = "https://www.ximalaya.com/revision/play/v1/audio?id=202502304&ptype=1"
        hutf = self.get_hutf(url)
        echo(json.dumps(json.loads(hutf), indent=2))


if __name__ == '__main__':
    start(XIMALAYA)
