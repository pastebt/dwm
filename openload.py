#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import sys
import json
import base64
from subprocess import Popen, PIPE
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
 

from comm import DWM, match1, echo, start, get_kind_size
from mybs import MyHtmlParser, select


class MSU(DWM):     #http://moviesunusa.net/
    cookie_fn = "msu_cookie.txt"
    login_url = 'http://moviesunusa.net/wp-login.php'

    def __init__(self):
        DWM.__init__(self)
        # remove cookie_fn
        os.remove(self.cookie_fn)

    def get_cookie(self):
        if os.path.exists(self.cookie_fn):
            return
        # first we need pass DDoS protection by CloudFlare
        echo("Wait 10 seconds ...")
        p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
                   "dwm.js", "-10", self.login_url], stdout=PIPE)
        p.stdout.read()
        p.wait()

    def query_info(self, url):
        self.get_cookie()
        # then we try to login
        #url = 'http://moviesunusa.net/%E7%8E%8B%E5%86%A0-%E7%AC%AC1%E5%AD%A3-%E7%AC%AC7%E9%9B%86-s1-ep7/'
        #post_data = 'log=sun03&pwd=sun&wp-submit=Login+%E2%86%92&redirect_to=http%3A%2F%2Fmoviesunusa.net%2F%25E7%258E%258B%25E5%2586%25A0-%25E7%25AC%25AC1%25E5%25AD%25A3-%25E7%25AC%25AC7%25E9%259B%2586-s1-ep7%2F'
        post_data = "log=sun03&pwd=sun&wp-submit=Login+%E2%86%92&redirect_to="
        post_data = post_data + urllib.quote(url)
        p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
                   "dwm.js", "20", self.login_url, url, post_data],
                  stdout=PIPE)
        echo("Wait 20 seconds ...")
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #echo(hutf)
        #
        #<meta name="og:url" content="https://openload.co/embed/isCWWnlsZLE/">
        #<iframe src="https://openload.co/embed/isCWWnlsZLE/" 
        urls = match1(hutf, '\<iframe src="(https://openload.co/embed/\S+)" ',
          '\<meta name="og:url" content="(https://openload.co/embed/\S+)"\>')
        echo(urls)

        title = match1(hutf, '<meta name="description" content="([^<>]+)">')
        echo(title)

        #return title, k, urls, total_size
        ol = OpenLoad()
        ol.title = title
        return ol.query_info(urls[0])


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
    start(MSU)
    #start(OpenLoad)
