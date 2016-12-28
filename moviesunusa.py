# -*- coding: utf8 -*-

import os
import re
import sys
from subprocess import Popen, PIPE
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
 
from openload import OpenLoad
from mybs import MyHtmlParser, SelStr
from comm import DWM, match1, echo, start, debug


class MSU1(DWM):     #http://moviesunusa.net/
    # using captcha, so this is usless, we use login_cookie and login_agent
    #handle_list = ['/moviesunusa.net/']
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

class MSU(DWM):     #http://moviesunusa.net/
    # using captcha, we use login_cookie and login_agent
    handle_list = ['/moviesunusa\.net/']

    def query_info(self, url):
        #url = 'http://moviesunusa.net/%e7%84%a1%e8%ad%89%e5%be%8b%e5%b8%ab-%e8%a8%b4%e8%a8%9f%e9%9b%99%e9%9b%84-%e7%ac%ac3%e5%ad%a3-%e7%ac%ac8%e9%9b%86-suits-s3-ep8/'
        if not self.login_cookie or not self.login_agent:
            echo('Pls setup cookie and login_agent')
            sys.exit(1)
        self.extra_headers['Cookie'] = self.login_cookie
        self.extra_headers['User-Agent'] = self.login_agent
        hutf = self.get_hutf(url)
        ifm = match1(hutf, '(\<iframe id="dmPlayer"[^\<\>]+\>\</iframe\>)')
        if ifm:
            u = SelStr('iframe', ifm)[0]['src']
            debug(u)
            if '/www.dailymotion.com/embed/video/' in u:
                from dailymotion import DM
                return DM().query_info(u)
            else:
                echo(u)
                raise Exception('need supporting new1 source')
                #sys.exit(1)
        nodes = SelStr('iframe', hutf)
        if nodes:
            u = nodes[0]['src']
            title = SelStr('meta[name=description]', hutf)[0]['content']
            debug(title)
            if 'openload.' in u:
                ol = OpenLoad()
                ol.title = title
                return ol.query_info(u)
            if 'rapidvideo.com/embed/' in u:
                from rapidvideo import RapidVideo
                rv = RapidVideo()
                rv.title = title
                return rv.query_info(u)
            else:
                echo(u)
                raise Exception('need supporting new2 source')
                #sys.exit(1)
        raise Exception('need supporting new3 source')
        #sys.exit(1)

    def get_playlist(self, url):
        urls = []
        self.extra_headers['Cookie'] = self.login_cookie
        self.extra_headers['User-Agent'] = self.login_agent
        hutf = self.get_hutf(url)
        for n in SelStr("div.yarpp-related > div > font > ul > li > "
                        "strong > a[rel=bookmark]", hutf):
            urls.append((n['title'], n['href']))
        return [x for x in reversed(urls)]

    def test(self):
        cookie = '__cfduid=dc0e31429acf4437138e0f0a21e6f0e861481002357; cf_clearance=e3deea1982cebbde2241fb46294cbdf1db69ab5f-1481002392-31536000; PHPSESSID=123ebb1be84b8fe46b4cd4b8f3d0a247; wordpress_test_cookie=WP+Cookie+check; wordpress_logged_in_a5b64ad7442ae4da2d093cd3469428ca=mo4%7C1482770286%7CgnHDig7f0KiTAyJSS0zXdobrRhs6jB5QJIDmbyrMFoT%7C9ce3dc4a93bf5aa64a64f64b72896fed02919ce5fd2440d0192ba4b346d0e31b; _ga=GA1.2.789626336.1481002395; _gat=1; _gat_clientTracker=1'
        #url = 'http://moviesunusa.net/%e7%84%a1%e8%ad%89%e5%be%8b%e5%b8%ab-%e8%a8%b4%e8%a8%9f%e9%9b%99%e9%9b%84-%e7%ac%ac3%e5%ad%a3-%e7%ac%ac8%e9%9b%86-suits-s3-ep8/'
        url = 'http://moviesunusa.net/%e7%84%a1%e8%ad%89%e5%be%8b%e5%b8%ab-%e8%a8%b4%e8%a8%9f%e9%9b%99%e9%9b%84-%e7%ac%ac5%e5%ad%a3-%e7%ac%ac11%e9%9b%86-suits-s5-ep11/'
        self.extra_headers['Cookie'] = cookie
        #self.extra_headers['Upgrade-Insecure-Requests'] = 1
        #self.extra_headers['Referer'] = 'http://moviesunusa.net/%E7%84%A1%E8%AD%89%E5%BE%8B%E5%B8%AB-%E7%AC%AC4%E5%AD%A3-suits-season-4/'
        self.extra_headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
        hutf = self.get_hutf(url, raw=True)
        
        comm.debug(hutf)


if __name__ == '__main__':
    #start(MSU)
    import comm
    comm.DEBUG = True
    MSU().test()
