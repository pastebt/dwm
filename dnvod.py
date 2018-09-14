# -*- coding: utf8 -*-

import os
import re
import sys
import json

from mybs import SelStr
from chrome import get_ci
from comm import DWM, match1, echo, start, debug, get_kind_size


class DNVOD(DWM):     # http://dnvod.eu/
    handle_list = ['dnvod']

    def query_info(self, url):
        return self.query_info_chrome(url)

    def query_info_chrome(self, url):
        ci = get_ci(debug)
        sel = "#ckplayer_a1"
        #ci = get_ci()
        ci.Page.navigate(url=url)
        ci.wait_event("Page.loadEventFired", timeout=60)
        ci.DOM.getDocument()
        res = ci.DOM.querySelector(nodeId=1, selector=sel)
        ni = res['result']['nodeId']
        ci.DOMDebugger.setDOMBreakpoint(nodeId=ni, type="attribute-modified")
        ci.wait_event("Debugger.paused", timeout=100)
        ci.Debugger.stepOut()
        res = ci.DOM.getAttributes(nodeId=ni)
        attrs = res['result']['attributes']
        attrs = dict(zip(attrs[::2], attrs[1::2]))
        src = attrs['src']
        # try title
        res = ci.DOM.querySelector(nodeId=1, selector="html head title")
        ni = res['result']['nodeId']
        res = ci.DOM.describeNode(nodeId=ni, depth=-1)
        title = res['result']['node']['children'][0]["nodeValue"].strip()
        return title, None, [src], None

    def query_info1(self, url):
        #url = 'https://www.dnvod.eu/Movie/Readyplay.aspx?id=deYM01Pf0bo%3d'
        hutf = self.get_hutf(url)
        title = SelStr('span#bfy_title >', hutf)[0].data.strip()
        debug('title =', title)
        for script in SelStr('script', hutf):
            txt = script.text
            debug('txt =', txt)
            if 'PlayerConfig' not in txt:
                continue
            debug('got PlayerConfig')
            vid = match1(txt, "id:\s*'([^']+)',")
            key = match1(txt, "key:\s*'([^']+)',")
            debug('vid =', vid, ', key =', key)
            break
        u = "https://www.dnvod.eu/Movie/GetResource.ashx?id=%s&type=htm" % vid
        self.extra_headers['Referer'] = url
        durl = self.get_html(u, postdata="key=" + key)
        debug(durl)
        return title, None, [durl], None

    def get_playlist(self, url):
        #url = 'https://www.dnvod.eu/Movie/detail.aspx?id=NU%2bOQHwQObI%3d'
        #url = 'https://www.dnvod.eu/Movie/Readyplay.aspx?id=deYM01Pf0bo%3d'
        hutf = self.get_hutf(url)
        urls = []
        for a in SelStr('ul[data-identity=guest] > li > div.bfan-n > a', hutf):
            debug(a.text, a['href'])
            urls.append((a.text, 'https://www.dnvod.eu' + a['href']))
        return urls

    def test(self, argv):
        url = 'https://www.dnvod.tv/Movie/detail.aspx?id=TEee8%2fITNg4%3d'
        url = 'https://www.dnvod.tv/Movie/Readyplay.aspx?id=OIfaQTVHEiA%3d'
        ru = 'http://server3.dnvod.tv/hvod/lxj-tscgwlb-50-022061041.mp4?sourceIp=154.20.114.142&signature=856ddbf8ecd34fb9b3aae7ad4c8beddf.56b9f1609633f7eacbc18ecd0dd5e4be&start=1536543792.79147&custom=0&ua=62e66f1213d2881d9f80510593ffe2ec'
        #ru = 'http://server3.dnvod.tv/hvod/lxj-tscgwlb-50-022061041.mp4'
        #hutf = self.get_hutf(url)
        #hutf = self.chrome_hutf(url)
        #echo(hutf)
        echo(get_kind_size(ru))


if __name__ == '__main__':
    start(DNVOD)
