#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
import json
import base64
try:
    import urllib.parse as urllib
except ImportError:
    import urllib

from mybs import MyHtmlParser, select
from comm import DWM, match1, echo, start, get_kind_size


class HYG(DWM):     #http://haiuken.com/ 海宇根
    def query_info(self, url):
        # http://haiuken.com/theatre/2muu/
        vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        echo("vid=", vid)
        html = self.get_html(url)
        #echo(html)
        hutf = html.decode('utf8', 'ignore')
        m = MyHtmlParser(tidy=False)
        m.feed(hutf)
        if self.title == "Unknown":
            title = m.select("head title")[0].text
            if title.startswith("Theatre - "):
                title = title[10:]
        else:
            title = self.title
        echo(title)

        ret = m.select(".bg2 .tmpl img")
        ips = json.dumps([r['src'].split("://")[1].split('/')[0] for r in ret])
        #echo(ips)

        d = {"xEvent": "UIMovieComments.Error",
             "xJson": ips}
        html = self.get_html("http://haiuken.com/ajax/theatre/%s/" % vid,
                             data=urllib.urlencode(d).encode("utf8"))
        ret = json.loads(html.decode('utf8'))
        url = base64.b64decode(ret['Data']['Error'].encode('utf8'))
        #echo(url)

        urls = [url.decode('utf8')]
        #echo(urls)
        k, total_size = get_kind_size(urls[0])
        k = k.split('/')[-1]
        #echo(k)
        echo(total_size)
        return title, k, urls, total_size


if __name__ == '__main__':
    start(HYG)
