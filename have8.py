# -*- coding: utf8 -*-

import re
import sys
try:
    from urllib import unquote
    from urlparse import urlparse
except ImportError:
    from urllib.parse import unquote, urlparse

from qq import QQ
from mybs import SelStr
from youku import YOUKU
from dailymotion import DM
from openload import OpenLoad
from comm import DWM, match1, echo, start, debug


def h8decode(a, b):
    ss = ""
    l = len(b) + 1
    for i, s in enumerate(a):
        if 0 == i % l:
            ss += s
    return unquote("".join(reversed(ss))).split('+++')


class HAVE8(DWM):     # http://have8.com/
    #handle_list = ['have8tv\.com/v/(drama|movie)/\d+/\d+/'
    #               '(dailymotion|youku|openload|qq|14tv)\.html',
    #               'v\.have8\.tv/drama/\d+/\d+/m3u8\.html']
    handle_list = ['have8\.tv/(drama|movie)/\d+/\d+/'
                   '(dailymotion|youku|openload|qq|14tv|m3u8)\.html',
                   'autocarinsider\.com/(d)/\d+/\d+/(m3u8)\.html',
                   ]

    def get_vsrc(self, hutf):
        m = re.search('var vsource = "([^"]+)";', hutf)
        return m.group(1)

    def get_vid(self, hutf, idx=''):
        m = re.search('adrss\[0\] \= "([^"]+)"', hutf)
        data = m.group(1)
        vids = h8decode(data, self.get_vsrc(hutf))
        vids = [v.split('++') for v in vids]
        if not idx:
            return vids
        for i, v in vids:
            #echo(repr(i), repr(idx))
            if int(i) == int(idx):
                return v
        return None

    def query_info(self, url):
        #if '/v/drama/' in url:
        #    return self.query_info_drama(url)
        #if '/v/movie/' in url:
        #    return self.query_info_movie(url)
        if '.tv/drama/' in url or '.com/d/' in url:
            return self.query_info_drama(url)
        if '.tv/movie/' in url:
            return self.query_info_movie(url)
        return None

    def query_info_drama_m3u8(self, url):
        # http://v.have8.tv/drama/2/25832/m3u8.html?0-29-0
        # https://52dy.hanju2017.com/20180904/BN0R4K7Y/index.m3u8
        hutf = self.get_hutf(url)
        idx = self.get_idx(url)
        debug("idx=", idx)
        m = re.search('var title = "([^"]+)";', hutf)
        debug("m =", m.group(1))
        title = m.group(1) + "_E%02d" % int(idx)
        vid = self.get_vid(hutf, idx)
        vid = unquote(vid)
        debug("vid =", vid)
        urls = self.try_m3u8(vid)
        debug("urls =", len(urls), urls[0])
        return title, None, urls, None

    def get_idx(self, url):
        up = urlparse(url)
        sels = up.query.split('-')
        debug("sels =", sels)
        idx = 1
        if len(sels) > 1:
            idx = sels[1]
        return idx

    def query_info_drama(self, url):
        #url = "http://have8tv.com/v/drama/2/21852/dailymotion.html?0-1-0"
        hutf = self.get_hutf(url)
        #up = urlparse(url)
        #sels = up.query.split('-')
        #debug("sels =", sels)
        #idx = 1
        #if len(sels) > 1:
        #    idx = sels[1]
        source = self.get_vsrc(hutf)
        if source == 'm3u8':
            return self.query_info_drama_m3u8(url)
        idx = self.get_idx(url)
        title = SelStr('meta[name=description]', hutf)[0]['content']
        title = title + "_E%02d" % int(idx)
        vid = self.get_vid(hutf, idx)
        debug('vid =', vid)
        debug('source =', source)
        if source == 'dailymotion':
            u = 'http://www.dailymotion.com/embed/video/' + vid
            return DM().query_info(u)
        elif source == 'youku':
            u = 'http://player.youku.com/embed/' + vid
            return YOUKU().query_info(u)
        elif source == 'openload':
            ol = OpenLoad()
            ol.title = title
            echo("using have8 title", title)
            u = 'https://openload.co/embed/' + vid
            return ol.query_info(u)
        elif source == 'qq':
            q = QQ()
            q.title = title
            echo("using have8 title", title)
            u = 'http://v.qq.com/iframe/player.html?vid=%s&tiny=0&auto=0' % vid
            #u = 'http://v.qq.com/iframe/player.html?vid=' + vid
            return q.query_info(u)
        elif source == '14tv':
            urls = self.query_14tv(vid)
            return title, None, urls, None

        echo("Found new source", source)
        sys.exit(1)

    def query_14tv(self, vid):
        bu = "http://v-redirect.14player.com/14tv/mp4:%s.mp4/" % vid
        us = self.try_m3u8(bu + "chunklist.m3u8")
        return [bu + u for u in us]

    def query_info_movie(self, url):
        #http://have8tv.com/v/movie/4/43601/dailymotion.html?0-1-0
        hutf = self.get_hutf(url)
        vids = self.get_vid(hutf, 1).split('+')
        debug('vids =', vids)
        urls = []
        for vid in vids:
            u = 'http://www.dailymotion.com/embed/video/' + vid
            t, e, us, z = DM().query_info(u)
            urls += us
        return t, e, urls, None

    def get_playlist(self, url):
        #url = "http://have8tv.com/v/drama/2/21852/dailymotion.html?0-1-0"
        up = urlparse(url)
        sels = up.query.split('-')
        if len(sels) < 2:
            sels = ['0', '', '0']
        hutf = self.get_hutf(url)
        vids = self.get_vid(hutf)
        urls = []
        base = up.scheme + '://' + up.netloc + up.path
        for vid in vids:
            sels[1] = vid[0]
            urls.append((None, base + "?" + '-'.join(sels)))
        return urls

    def test(self):
        #not support
        # http://have8tv.com/v/movie/4/43601/dailymotion.html?0-1-0
        #url = 'http://have8tv.com/v/drama/2/25076/youku.html?0-3-0'
        #url = 'http://have8tv.com/v/movie/4/43601/dailymotion.html?0-1-0'
        #url = 'http://have8tv.com/v/drama/2/25583/openload.html?0-1-0'
        #url = 'http://have8tv.com/v/drama/1/19161/qq.html?0-1-0'
        #url = 'http://have8tv.com/v/drama/2/20636/14tv.html?0-1-0'
        #http://v-redirect.14player.com/14tv/mp4:lxj-agxqd6j-01.mp4/chunklist.m3u8
        #url = "http://v.have8.tv/drama/2/25832/m3u8.html?0-29-0"
            # https://52dy.hanju2017.com/20180904/BN0R4K7Y/index.m3u8
        url = "http://autocarinsider.com/d/2/28239/m3u8.html?0-10-0"
        hutf = self.get_hutf(url)
        echo(hutf)
        vids = self.get_vid(hutf)
        echo(vids)
        vid = vids[0]
        #vid = self.get_vid(hutf, idx)
        #debug('vid =', vid)
        source = self.get_vsrc(hutf)
        echo("source", source)
        #url = "http://v-redirect.14player.com/14tv/mp4:%s.mp4/chunklist.m3u8" % vid[1]
        #echo(url)
        #hutf = self.get_hutf(url)
        #print hutf
        #us = self.try_m3u8(url)
        #echo(us)


if __name__ == '__main__':
    #start(HAVE8)
    HAVE8().test()
