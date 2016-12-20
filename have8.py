# -*- coding: utf8 -*-

import os
import re
import sys
from subprocess import Popen, PIPE
 
from mybs import SelStr
from comm import DWM, match1, echo, start


class HAVE8(DWM):     # http://have8.com/
    #handle_list = ['openload']
    cookie_fn = "have8_cookie.txt"

    def __init__(self):
        DWM.__init__(self)
        #self.extra_headers['Referer'] = 'https://vjs.zencdn.net/swf/5.1.0/video-js.swf'
        self.extra_headers['Upgrade-Insecure-Requests'] = '1'
        

    def clean_up(self):
        if os.path.exists(self.cookie_fn):
            os.remove(self.cookie_fn)

    def query_info(self, url):
        # get vid url
        self.extra_headers['Referer'] = "http://have8tv.com/v/drama/2/21852/dailymotion.html?0-1-0"
        rurl = 'http://www.dailymotion.com/embed/video/k7alsxAgBgcMGaachYS?api=postMessage&autoplay=0&info=0'
        hutf = self.get_hutf(rurl)
        #echo(hutf)
        m = re.search('''"ad_url":"([^"]+)"''', hutf)
        aurl = m.groups()[0].replace('\\', '') #+ '&ps=658x435&ct=website&callback=jsonp_1482257169574_88239'
        echo(aurl)
        # "720":[{"type":"application\/x-mpegURL","url":"http:\/\/www.dailymotion.com\/cdn\/manifest\/video\/x2hpv0i.m3u8?auth=1482432896-2562-0fq84z9d-24047244e9a36f0f3fab8388642b74c1&include=720"},{"type":"video\/mp4","url":"http:\/\/www.dailymotion.com\/cdn\/H264-1280x720\/video\/x2hpv0i.mp4?auth=1482432896-2562-pvg451ll-4c251ca9aa8a1bf6f56c88d318eccd65"}]}
        m = re.search('/x-mpegURL","url":"([^"]+)"', hutf)
        vurl = m.groups()[0].replace('\\', '')
        self.extra_headers['Referer'] = rurl
        # using ad url set cookie
        hutf = self.get_hutf(aurl)
        # get m3u8 list
        hutf = self.get_hutf(vurl)
        echo(hutf)
        sys.exit(1)

    def query_info1(self, url):
        self.clean_up()
        # http://v.have8.com/drama/2/21852-维京传奇第三季/
        url = "http://have8tv.com/v/drama/2/21852/dailymotion.html?0-1-0"
        #echo(self.get_hutf(url))
        #sys.exit(1)

        echo("phantomjs wait 300 ...")
        p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
                   "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #m = re.search('''"ad_url":"([^"]+)"''', hutf)
        #aurl = m.groups()[0].replace('\\', '') + '&ps=658x435&ct=website&callback=jsonp_1482257169574_88239'
        #echo(aurl)
        nodes = SelStr("div.bf_swf_flash > iframe", hutf)
        rurl = nodes[0]['src']
        echo(rurl)
        ##self.extra_headers['Referer'] = rurl
        ##hutf = self.get_hutf(aurl)
        ##hutf = self.get_hutf(url)
        #echo("phantomjs aurl wait 300 ...")
        p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
                   "dwm.js", "300", rurl, url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #echo(hutf)

        #url = 'http://www.dailymotion.com/cdn/manifest/video/x2hpv0i.m3u8?auth=1482429895-2688-mdq7s6vu-184adab1604edea4c3f0b59243b19554'
        #echo("phantomjs url wait 300 ...")
        #p = Popen(["./phantomjs", "--cookies-file", self.cookie_fn,
        #           "dwm.js", "300", url, rurl], stdout=PIPE)
        #html = p.stdout.read()
        #hutf = html.decode('utf8')
        #p.wait()
        #echo(hutf)
        sys.exit(1)

        #return self.title, k, [url], tsize


if __name__ == '__main__':
    start(HAVE8)
