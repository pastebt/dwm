#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
#from subprocess import Popen, PIPE
#from html.parser import HTMLParser

from mybs import SelStr
from comm import DWM, match1, echo, start, get_kind_size, USER_AGENT


class DYB(DWM):     #dianyingbar
    def __init__(self):
        # http://www.dianyingbar.com/10085.html
        DWM.__init__(self)
        self.extra_headers = {"User-Agent": USER_AGENT,
                              'Upgrade-Insecure-Requests': '1',
                              'Referer': "http://bodekuai.duapp.com/ckplayer/ckplayer.swf"}

    def query_info(self, url):
        # get flv part list
        html = self.get_html(url)
        hutf = html.decode('utf8', 'ignore')
        #echo(hutf)
        ret = re.findall("<video><file><\!\[CDATA\[([^<>]+)\]\]></file>"
                         "<size>(\d+)</size>"
                         "<seconds>\d+</seconds></video>",
                         hutf)
        print(ret)
        if not ret:
            return self.qi2(hutf)
        urls = []
        total_size = 0
        for u, s in ret:
            urls.append(u)
            total_size += int(s)
        if urls:
            k, s = get_kind_size(urls[0])
            k = k.split('/')[-1]
        else:
            k = ''
        #echo(k)
        #return
        return None, k, urls, total_size

    def qi2(self, hutf):
        # http://www.dianyingbar.com/11184.html
        ret = re.findall("videoarr.push\('YKYun\.php\?id\=([^\(\)]+)'\)", hutf)
        echo(ret)
        ns = SelStr('article.article-content > p > strong', hutf)
        title = ns[0].text
        urls = []
        tsize = 0
        for vid in ret:
            url = 'https://vipwobuka.dianyingbar.com:998/api/yUrl.php?id=%s&type=mp4' % vid
            #self.extra_headers['Referer'] = 'https://vipwobuka.dianyingbar.com:998/ckplayer/YKYun.php?id=' + vid
            k, s = get_kind_size(url)
            tsize += s
            urls.append(url)
            break
        echo("kind=", k[-3:], "size=", tsize, "title=", title)
        return title, k[-3:], urls, tsize


    def try_playlist(self, ispl, url):
        # http://www.dianyingbar.com/9111.html
        # http://www.dianyingbar.com/3970.html
        # get xml
        html = self.get_html(url)
        hutf = html.decode('utf8', 'ignore')
        ret = re.findall("videoarr.push\('YKYun\.php\?id\=([^\(\)]+)'\)", hutf)
        #print(ret[0])
        t = self.title
        #pl = ["http://bodekuai.duapp.com/api/yUrl.php?id=" + r for r in ret]
        pl = []
        for i, r in enumerate(ret, start=1):
            pl.append(("%s_%02d" % (t, i),
                       "http://bodekuai.duapp.com/api/yUrl.php?id=" + r))
        echo(pl)
        return pl


# failed
# http://www.dianyingbar.com/11151.html


if __name__ == '__main__':
    start(DYB)
