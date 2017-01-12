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

from mybs import MyHtmlParser
from comm import DWM, match1, echo, start, get_kind_size, UTITLE


class HYG(DWM):     #http://haiuken.com/ 海宇根
    handle_list = ['/haiuken.com/']

    def query_info(self, url):
        # http://haiuken.com/theatre/2muu/
        vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        echo("vid=", vid)
        hutf = self.get_hutf(url)
        m = MyHtmlParser(tidy=False)
        m.feed(hutf)
        if self.title == UTITLE:
            title = m.select("head title")[0].text
            if title.startswith("Theatre - "):
                title = title[10:]
        else:
            title = self.title

        ret = m.select(".bg2 .tmpl img")
        ips = json.dumps([r['src'].split("://")[1].split('/')[0] for r in ret])

        d = {"xEvent": "UIMovieComments.Error",
             "xJson": ips}
        hutf = self.get_html("http://haiuken.com/ajax/theatre/%s/" % vid,
                             postdata=urllib.urlencode(d).encode("utf8"))
        ret = json.loads(hutf)
        url = base64.b64decode(ret['Data']['Error'].encode('utf8')).decode('utf8')
        return title, None, [url], None


if __name__ == '__main__':
    start(HYG)
