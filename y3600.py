# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, get_kind_size


class Y3600(DWM):
    handle_list = ['www.y3600.com/']

    def query_info(self, m3u8url):
        hutf = self.get_hutf(m3u8url)
        #echo(hutf)
        #url = "https://www.y3600.com/hanju/2017/1017.html"
        m = re.findall('''var redirecturl = "(.+)";''', hutf)
        if m:
            echo(m)
            b = m[0]
            m = re.findall('''var main = "(.+index.m3u8.+)";''', hutf)
            echo(m)
            m3u8url = b + m[0]
 
        us = self.try_m3u8(m3u8url)

        #echo(us)
        #if len(us) == 1:
        #    t, s = get_kind_size(us[0])
        #    if t == 'm3u8':
        #        us = self.try_m3u8(us[0])

        #us = self._read_m3u8(m3u8url)
        #print(us)
        #us = self._read_m3u8(us[0])
        #print(us)
        return "", None, us, None

    #def _read_m3u8(self, url):
    #    hutf = self.get_hutf(url)
    #    bu = os.path.dirname(url) + "/"
    #    rt = "/".join(url.split('/')[:3])
    #    urls = []
    #    for line in hutf.split('\n'):
    #        line = line.strip()
    #        if not line or line.startswith("#"):
    #            continue
    #        if "://" in line:
    #            urls.append(line)
    #        elif line[0] == '/':
    #            urls.append(rt + line)
    #        else:
    #            urls.append(bu + line)
    #    return urls

    def get_playlist(self, url):
        #url = 'https://www.y3600.com/hanju/2014/374.html?ing=4#play'
        hutf = self.get_hutf(url)
        m = re.findall('''<a onclick="ck_m3u8\('([^<>]+)',this.+title="([^<>]+)">''', hutf)
        if len(m) > 0:
            return [(x[1], x[0]) for x in m]
        #return
        us = self._doif(hutf)
        return us

    def _doif(self, hutf):
        #url = "https://www.y3600.com/hanju/2017/1017.html"
        m = re.findall('''<a onclick="doif\('([^<>]+)'.+title="([^"]+)".*>''', hutf)
        echo(m)
        return [(x[1], x[0]) for x in m]

        us = []
        for u, t in m:
            echo(u)
            # var redirecturl = "http://v2.438vip.com";
            # var main = "/20170506/GwFE9JWN/index.m3u8?sign=6afb22db55a3e57908ae61c92b5d8a7ef8dc83032480fa7053da8894ca59e41f64b650d5000a87a8b99b66c829ee8513bed34740982d1bc9e924c752a8d01ce3";
            hutf = self.get_hutf(u)
            #echo(hutf)
            m = re.findall('''var redirecturl = "(.+)";''', hutf)
            echo(m)
            b = m[0]
            m = re.findall('''var main = "(.+index.m3u8.+)";''', hutf)
            echo(m)
            url = b + m[0]
            echo(url)
            us.append((t, url))
        return us

    def test1(self, args):
        #url = 'https://www.y3600.com/hanju/2014/374.html?ing=4#play'
        #url = "https://www.y3600.com/hanju/2018/1366.html"
        url = "https://www.y3600.com/hanju/2014/333.html"   # failed
        #self.query_info(url)
        #hutf = self.get_hutf(url)
        hutf = self.phantom_hutf(url)
        echo(hutf)
        #<a onclick="ck_m3u8('http://n.bwzybf.com:80/20171217/Zx0y6FM8/index.m3u8',this);" href="#play" title="《KillmeHealme》第02集">
        m = re.findall('''<a onclick="ck_m3u8\('([^<>]+)',this.+title="([^<>]+)">''', hutf)
        echo(m)
        #us = self._get_m3u8_urls(m[0][0], self.get_hutf(m[0][0]))
        #us = self._read_m3u8(m[0][0])
        us = self.try_m3u8(m[0][0])
        echo(us[0])
        echo(get_kind_size(us[0]))
        #us = self._read_m3u8(us[0])
        #echo(us)
        #us = self._get_m3u8_urls(us, self.

    def test2(self, args):
        url = "https://www.y3600.com/hanju/2017/1017.html"
        hutf = self.get_hutf(url)
        #m = re.findall('''<a onclick="doif\('([^<>]+)',this.+title="([^<>]+)" ing.+>''', hutf)
        m = re.findall('''<a onclick="doif\('([^<>]+)'.+title="([^"]+)".*>''', hutf)
        echo(m)
        u = m[0][0]
        echo(u)
        # var redirecturl = "http://v2.438vip.com";
        # var main = "/20170506/GwFE9JWN/index.m3u8?sign=6afb22db55a3e57908ae61c92b5d8a7ef8dc83032480fa7053da8894ca59e41f64b650d5000a87a8b99b66c829ee8513bed34740982d1bc9e924c752a8d01ce3";
        hutf = self.get_hutf(u)
        #echo(hutf)
        m = re.findall('''var redirecturl = "(.+)";''', hutf)
        echo(m)
        b = m[0]
        m = re.findall('''var main = "(.+index.m3u8.+)";''', hutf)
        echo(m)
        url = b + m[0]
        echo(url)
        us = self.try_m3u8(url)
        echo(us)
        us = self.try_m3u8(us[0])
        echo(us)

    def test(self, args):
        url = "https://www.y3600.com/hanju/2014/334.html"
        url = "https://www.y3600.com/hanju/2014/367.html"
        hutf = self.get_hutf(url)
        echo(hutf)


if __name__ == '__main__':
    start(Y3600)
