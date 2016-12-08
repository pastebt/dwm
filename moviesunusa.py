#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
 
from openload import OpenLoad
from mybs import MyHtmlParser
from comm import DWM, match1, echo, start


class MSU(DWM):     #http://moviesunusa.net/
    cookie_fn = "msu_cookie.txt"
    login_url = 'http://moviesunusa.net/wp-login.php'

    def __init__(self):
        DWM.__init__(self)
        # remove cookie_fn
        if os.path.exists(self.cookie_fn):
            os.remove(self.cookie_fn)

    def clean_up(self):
        if os.path.exists(self.cookie_fn):
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

    def try_playlist(self, ispl, url):
        p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
                   "dwm.js", "-10", url], stdout=PIPE)
        echo("Wait 10 seconds ...")
        html = p.stdout.read()
        p.wait()
        hutf = html.decode('utf8', 'ignore')
        #echo(hutf)
        #return 1
        #hutf = open("a.html").read()
        mp = MyHtmlParser(tidy=False)
        mp.feed(hutf)
        # body > div.mh-container > div.mh-wrapper.clearfix > div > div > article > div.entry.clearfix > div > div > font > ul > li:nth-child(1) > strong > a
        nodes = mp.select("div.yarpp-related > div > font > ul > li > strong > a")
        urls = []
        for n in nodes:
            if n['rel'] == 'bookmark':
                urls.append((n['title'], n['href']))
        urls = [x for x in reversed(urls)]
        for t, u in urls:
            echo(t, u)
        if urls:
            return urls
        return None


if __name__ == '__main__':
    start(MSU)
