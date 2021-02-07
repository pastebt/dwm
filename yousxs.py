# -*- coding: utf8 -*-

import re
import json
from subprocess import Popen, PIPE

from mybs import SelStr
from chrome import get_ci
from comm import DWM, echo, start, match1, norm_url, debug


class YOUSXS(DWM):
    handle_list = ['(/|\.)yousxs\.com/']

    def query_info(self, url):
        #url = "https://www.yousxs.com/player/4659_1.html"
        ci = get_ci(debug())
        try:
            ci.Page.navigate(url=url)
            ci.wait_event("Page.loadEventFired", timeout=30)
            ret = ci.Runtime.evaluate(expression="ap.options.audio[0].name")
            title = ret["result"]["result"]["value"]
            ret = ci.Runtime.evaluate(expression="ap.options.audio[0].url")
            mp3url = ret["result"]["result"]["value"]
        finally:
            ci.stop()
        u = norm_url(mp3url)
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
       
    def test1(self, argv):
        url = "https://www.yousxs.com/4659.html"
        echo(self.get_playlist(url))
        mid = match1(url, "yousxs.com/(\d+).html")
        echo(mid)
        hutf = open("y_4659.html").read().decode("utf8")
        al = SelStr("div.panel-body div.col-xs-3 a", hutf)
        echo(al)
        for a in al:
            n = match1(a['href'], "player/4659_(\d+).html")
            if n is None:
                continue
            echo(n)

    def test(self, argv):
        url = "https://www.yousxs.com/4659.html"
        url = "https://www.yousxs.com/player/4659_1.html"
        #hutf = self.phantom_hutf(url)
        #echo(hutf)
        ci = get_ci(debug())
        try:
            ci.Page.navigate(url=url)
            ci.wait_event("Page.loadEventFired", timeout=30)
            ret = ci.Runtime.evaluate(expression="skey")
            #print(json.dumps(ret, indent=2))
            #print("skey =", ret["result"]["result"]["value"])
            ret = ci.Runtime.evaluate(expression="ap.options.audio[0].url")
            ret = ci.Runtime.evaluate(expression="ap.options.audio[0].name")
        finally:
            ci.stop()


if __name__ == '__main__':
    start(YOUSXS)
