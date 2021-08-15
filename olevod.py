# -*- coding: utf8 -*-

import sys
import json

from mybs import SelStr
from chrome import get_ci
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from comm import DWM, start, debug, echo, match1


class OLEVOD(DWM):
    #no_check_certificate = True
    handle_list = ['(/|\.)olevod\.com/']
    m3u8_slow_merge = True

    def query_info(self, url):
        murl = self.find_murl(url)
        murl = self.last_m3u8(murl)
        debug(murl)
        title = self.get_title(url)
        return title, "m3u8", murl, None

    def get_title(self, url):
        hutf = self.get_hutf(url)
        t = SelStr("div.video_title h2.title", hutf)
        if t:
            return t[0].text
        return None

    def get_playlist(self, url):
        hutf = self.get_hutf(url)
        t = SelStr("div.video_title h2.title", hutf)
        title = "Unknown"
        if t:
            title = t[0].text
        ts = SelStr("div#playlistbox ul.content_playlist li a", hutf)
        return [(u"%s_%s" % (title, t.text), "https://www.olevod.com" + t['href']) for t in ts]

    def find_murl(self, url):
        #url = 'https://www.olevod.com/index.php/vod/play/id/24986/sid/1/nid/76.html'
        ci = get_ci()
        murl = ""

        qnrwb = Queue()
        def nrwb(ci, msg):
            u = msg['params']['request']['url']
            debug("Network.requestWillBeSent url", url)
            if 'master.m3u8' in u:
                debug("got master.m3u8", u)
                qnrwb.put(u)
        ci.reg("Network.requestWillBeSent", nrwb)
            
        try:
            ci.Page.navigate(url=url)
            murl = qnrwb.get(timeout=ci.get_to())
            debug("murl = ", murl)
            return murl
        #except Exception as e:
        #    echo("key_m3u8 out:", repr(e))
        finally:
            ci.close()

    def test(self, args):
        url = "https://www.olevod.com/index.php/vod/play/id/24986/sid/1/nid/75.html"
        for t in (self.get_playlist(url)):
            echo(t[0], t[1])
        #hutf = self.get_hutf(url)
        #echo(hutf)
        #self.title_murl(url)
        # https://europe.olemovienews.com/hlstimeofffmp4/20210503/xyflmsiG/mp4/xyflmsiG.mp4/master.m3u8


if __name__ == '__main__':
    start(OLEVOD)
