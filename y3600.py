# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, get_kind_size


class M3U8(DWM):
    handle_list = ['www.y3600.com/']

    def query_info(self, m3u8url):
        us = self.try_m3u8(m3u8url)
        echo(us)
        if len(us) == 1:
            t, s = get_kind_size(us[0])
            if t == 'm3u8':
                us = self.try_m3u8(us[0])
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
        return [(x[1], x[0]) for x in m]

    def test(self, args):
        url = 'https://www.y3600.com/hanju/2014/374.html?ing=4#play'
        #url = "https://www.y3600.com/hanju/2018/1366.html"
        #self.query_info(url)
        hutf = self.get_hutf(url)
        #<a onclick="ck_m3u8('http://n.bwzybf.com:80/20171217/Zx0y6FM8/index.m3u8',this);" href="#play" title="《KillmeHealme》第02集">
        m = re.findall('''<a onclick="ck_m3u8\('([^<>]+)',this.+title="([^<>]+)">''', hutf)
        #echo(m)
        #us = self._get_m3u8_urls(m[0][0], self.get_hutf(m[0][0]))
        #us = self._read_m3u8(m[0][0])
        us = self.try_m3u8(m[0][0])
        echo(us[0])
        echo(get_kind_size(us[0]))
        #us = self._read_m3u8(us[0])
        #echo(us)
        #us = self._get_m3u8_urls(us, self.


if __name__ == '__main__':
    start(M3U8)
