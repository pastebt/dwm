#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import random
from subprocess import Popen, PIPE
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
 
from openload import OpenLoad
from mybs import MyHtmlParser
from comm import DWM, match1, echo, start


class VMUS(DWM):     #http://vmus.co/
    login_url = 'http://vmus.co/wp-login.php'

    def query_info(self, url):
        # then we try to login
        #url = 'http://vmus.co/%E9%99%90%E5%88%B6%E7%B4%9A%E6%AF%92%E6%A2%9F-narcos-%E7%AC%AC%E4%B8%80%E5%AD%A3-%E7%AC%AC%E4%BA%94%E9%9B%86-s01e05-%E7%B7%9A%E4%B8%8A%E7%9C%8B-%E7%B0%A1%E4%B8%AD%E8%8B%B1%E5%AD%97%E5%B9%95/'
        #post_data = 'log=vm16&pwd=vm16&wp-submit=%E5%85%8D%E8%A8%BB%E5%86%8A%E7%99%BB%E5%85%A5%28%E6%96%B9%E6%B3%95%E8%AB%8B%E8%A6%8B%E4%B8%8A%E6%96%B9%E8%AA%AA%E6%98%8E%29+%C2%BB&redirect_to=%2F%25E9%2599%2590%25E5%2588%25B6%25E7%25B4%259A%25E6%25AF%2592%25E6%25A2%259F-narcos-%25E7%25AC%25AC%25E4%25B8%2580%25E5%25AD%25A3-%25E7%25AC%25AC%25E4%25BA%2594%25E9%259B%2586-s01e05-%25E7%25B7%259A%25E4%25B8%258A%25E7%259C%258B-%25E7%25B0%25A1%25E4%25B8%25AD%25E8%258B%25B1%25E5%25AD%2597%25E5%25B9%2595%2F'
        up = "vm%02d" % random.randint(1, 30)
        echo(up)
        post_data = "log=%s&pwd=%s&wp-submit=" % (up, up)
        post_data = post_data + "%E5%85%8D%E8%A8%BB%E5%86%8A%E7%99%BB%E5%85%A5%28%E6%96%B9%E6%B3%95%E8%AB%8B%E8%A6%8B%E4%B8%8A%E6%96%B9%E8%AA%AA%E6%98%8E%29+%C2%BB&redirect_to="
        post_data = post_data + urllib.quote(url)
        #p = Popen(["./phantomjs", "dwm.js", "60", self.login_url, url, post_data],
        #          stdout=PIPE)
        #echo("Wait query_info phantomjs 60 sec ...")
        #html = p.stdout.read()
        #p.wait()
        html = self.get_html(self.login_url, postdata=post_data)
        hutf = html.decode('utf8')
        #echo(hutf)
        #
        #<meta name="og:url" content="https://openload.co/embed/isCWWnlsZLE/">
        #<iframe src="https://openload.co/embed/isCWWnlsZLE/" 
        urls = match1(hutf, '\<iframe src="(https://openload.(c|i)o/embed/\S+)" ',
          '\<meta name="og:url" content="(https://openload.(c|i)o/embed/\S+)"\>')
        echo(urls)

        title = match1(hutf, '<meta property="og:title" content="([^<>]+)"')
        echo("vmus query_info title=", title)

        #return title, k, urls, total_size
        ol = OpenLoad()
        ol.title = title
        return ol.query_info(urls[0])

    def try_playlist(self, ispl, url):
        # http://vmus.co/category/%E9%80%A3%E8%BC%89%E4%B8%AD/%E7%AC%AC%E4%B8%80%E5%AD%A3/%E6%AF%92%E6%A2%9Fnarcos/
        #p = Popen(["./phantomjs", "dwm.js", "60", url], stdout=PIPE)
        #echo("Wait try_playlist phantomjs 60 sec ...")
        #html = p.stdout.read()
        #p.wait()
        html = self.get_html(url)
        hutf = html.decode('utf8', 'ignore')
        #echo(hutf)
        mp = MyHtmlParser(tidy=False)
        mp.feed(hutf)
        # #post-24821 > h2 > a #content
        nodes = mp.select("#content > article > h2 > a")
        urls = []
        for n in nodes:
            if n['rel'] == 'bookmark':
                urls.append((n.text, n['href']))
        urls = [x for x in reversed(urls)]
        if not urls:
            # http://vmus.co/%E7%BE%85%E9%A6%AC%E7%9A%84%E6%A6%AE%E8%80%80-rome/
            # #post-2644 > div.entry.clearfix > p:nth-child(11) > a:nth-child(1)
            #nodes = mp.select("#content article div.entry p a")
            #for n in nodes:
            #    urls.append((n.text, n['href']))

            # http://vmus.co/11-22-63/  has extra entry need filter out
            phrs = mp.select("#content article div.entry hr,p")
            h = False
            for n in phrs:
                if n.tag == 'hr':
                    h = True
                    continue
                if not h:
                    continue
                na = n.select('a')
                for a in na:
                    urls.append((a.text, a['href']))
 
        #urls.sort()
        for t, u in urls:
            echo(t, u)
        if urls:
            return urls
        echo("urls =", urls)
        return None


if __name__ == '__main__':
    start(VMUS)
