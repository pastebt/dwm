#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
import json
try:
    import urllib.parse as urllib
except ImportError:
    from urlparse import parse_qs, urlparse

import base64

from comm import DWM, match1, echo, start, get_kind_size
from mybs import MyHtmlParser, select


class ZSJ(DWM):     #http://www.zhusj.com/ 主视角
    def query_info(self, url):
        # http://www.zhusj.com/html/jq/3272.html?fromvsogou=1
        #vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        #echo("vid=", vid)
        html = self.get_html(url)
        #echo(html)
        hutf = html.decode('utf8', 'ignore')
        # <iframe src="http://api.ourder.com/video/ssl/player.aspx?c=06141e1c5a4c1e3c303b360531053e4a32185a4c1b5a4c1b&w=640&h=380
        #echo(hutf)
        #return
        m = MyHtmlParser(tidy=False)
        m.feed(hutf)
        ifs = m.select("iframe")
        for i in ifs:
            if 'api.ourder.com' in i['src']:
                url = i['src']
                echo(url)
                break
        tn = m.select('div.crumbs span')[0]
        title = tn.text
        echo(title)
        #return

        self.get_html(url)
        echo(self.get_html_url)
        #https://api.ourder.com/video/ssl/https.html?h=380px&id=CODIzNzA5Mg==
        #https://api.ourder.com/video/ssl/YkcrefHandler.ashx?id=xxx
        r = urlparse(self.get_html_url)
        q = parse_qs(r.query)
        if '/video/ssl/https.html' in self.get_html_url:
            vid = q['id'][0]
            echo(vid)
            #return
            url = 'https://api.ourder.com/video/ssl/YkcrefHandler.ashx?id=' + vid
        elif '/video/ssl/videoplayer.html' in self.get_html_url:
            #http://api.ourder.com/video/ssl/videoplayer.html?url=http://v.youku.com/v_show/id_XMTQ1MDM1MDc3Ng==.html?from=y1.12-96
            url = q['url'][0]

        k, total_size = get_kind_size(url)
        k = k.split('/')[-1]
        return title, k, [url], total_size


if __name__ == '__main__':
    start(ZSJ)
