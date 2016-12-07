#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
import json
from subprocess import Popen, PIPE
try:
    import urllib.parse as urllib
except ImportError:
    import urllib

import base64

from comm import DWM, match1, echo, start, get_kind_size
from mybs import MyHtmlParser, select


class MSU(DWM):     #http://moviesunusa.net/
    def query_info(self, url):
        url2 = 'http://moviesunusa.net/%E7%8E%8B%E5%86%A0-%E7%AC%AC1%E5%AD%A3-%E7%AC%AC7%E9%9B%86-s1-ep7/'
        #p = Popen(["./phantomjs", "dwm.js", "-20", url], stdout=PIPE)
        p = Popen(["./phantomjs", "--cookies-file", "msu_cookie.txt", "msu.js", "-30", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        echo(hutf)
        return

        #url = 'http://moviesunusa.net/wp-login.php'
        #html = self.get_html(url, data='log=sun03&pwd=sun&wp-submit=Login+%E2%86%92&redirect_to=http%3A%2F%2Fmoviesunusa.net%2F%25E7%258E%258B%25E5%2586%25A0-%25E7%25AC%25AC1%25E5%25AD%25A3-%25E7%25AC%25AC7%25E9%259B%2586-s1-ep7%2F'.encode('utf8'))
        #echo(html)
        return
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


class OpenLoad(DWM):     # http://openload.co/
    def __init__(self):
        DWM.__init__(self)
        self.extra_headers['Referer'] = 'https://vjs.zencdn.net/swf/5.1.0/video-js.swf'

    def query_info(self, url):
        # https://openload.co/embed/isCWWnlsZLE/
        # <span id="streamurl">isCWWnlsZLE~1481138074~208.91.0.0~g617lYdo</span>
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        m = re.search('''<span id="streamurl">([^<>]+)</span>''', hutf)
        vid = m.groups()[0]
        echo(vid)
        url = "https://openload.co/stream/%s?mime=true" % vid

        # https://openload.co/stream/isCWWnlsZLE~1481139117~208.91.0.0~mcLfSy5C?mime=true
        # video/mp4 584989307
        k, tsize = get_kind_size(url)
        k = k.split('/')[-1]
        return self.title, k, [url], tsize
        

if __name__ == '__main__':
    #start(MSU)
    start(OpenLoad)
