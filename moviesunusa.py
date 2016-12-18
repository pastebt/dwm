#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
 
from mybs import MyHtmlParser
from openload import OpenLoad
from comm import DWM, match1, echo, start


class MSU(DWM):     #http://moviesunusa.net/
    handle_list = ['/moviesunusa.net/']
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
        echo("Get Cookie Wait 10 seconds ...")
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
        echo("Query Info Wait 20 seconds ...")
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #echo(hutf)
        #
        #<meta name="og:url" content="https://openload.co/embed/isCWWnlsZLE/">
        #<iframe src="https://openload.co/embed/isCWWnlsZLE/" 
        urls = match1(hutf, '\<iframe src="(https://openload.(c|i)o/embed/\S+)" ',
          '\<meta name="og:url" content="(https://openload.(c|i)o/embed/\S+)"\>')
        echo(urls)

        title = match1(hutf, '<meta name="description" content="([^<>]+)">')
        echo(title)

        #return title, k, urls, total_size
        ol = OpenLoad()
        ol.title = title
        return ol.query_info(urls[0])

    def get_playlist(self, url):
        if re.search("-s\d+-ep\d+", url, re.I):
            return []
        p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
                   "dwm.js", "-10", url], stdout=PIPE)
        echo("Try Playlist Wait 10 seconds ...")
        html = p.stdout.read()
        p.wait()
        hutf = html.decode('utf8', 'ignore')
        mp = MyHtmlParser(tidy=False)
        mp.feed(hutf)
        nodes = mp.select("div.yarpp-related > div > font > ul > li > strong > a")
        urls = []
        for n in nodes:
            if n['rel'] == 'bookmark':
                urls.append((n['title'], n['href']))
        return [x for x in reversed(urls)]


if __name__ == '__main__':
    start(MSU)
