# -*- coding: utf8 -*-

import re
import sys
import json
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, debug


class KANTV6(DWM):
    handle_list = ['//kantv6\.com/', '//www\.kantv6\.com/']

    def query_info(self, url):
        title, mu = "", url
        if 'm3u8' not in url:
            title, mu = self.get_m3u8(url)
        us = self.try_m3u8(mu)
        return title, None, us, None

    def get_m3u8(self, url):
        # https://www.kantv6.com/tvdrama/301948271219001-161948271219033
        # https://www.kantv6.com/index.php/video/play?tvid=301948271219001&part_id=161948271219033&line=1&seo=tvdrama
        sect, tvid, ptid = self.get_stp(url)
        title = self.get_title(tvid, sect)
        du = "https://www.kantv6.com/index.php/video/play"
        if sect == 'movie':
            du = "%s?tvid=%s&line=1&seo=%s" % (du, tvid, sect)
        elif sect == 'tvdrama':
            if not ptid:
                echo("no ptid")
                return
            du = "%s?tvid=%s&part_id=%s&line=1&seo=%s" % (du, tvid, ptid, sect)
        else:
            echo("Unknown Sect", sect)
            return
        dat = self.get_hutf(du)
        dat = json.loads(dat)
        if sect == 'tvdrama':
            title = title + "_" + dat['data']['part_title']
        debug(json.dumps(dat, indent=2))
        echo("title", title)
        #return
        #us = self.try_m3u8('https:' + dat['data']['url'])
        #return title, None, us, None
        return title, 'https:' + dat['data']['url']

    def get_playlist(self, url):
        sect, tvid, ptid = self.get_stp(url)
        if sect != "tvdrama":
            return []
        u = 'https://www.kantv6.com/index.php/video/part'
        u = '%s?tvid=%s' % (u, tvid)
        t = self.get_title(tvid, sect)
        dat = self.get_hutf(u)
        dat = json.loads(dat)
        debug(json.dumps(dat, indent=2))
        #bu = 'https://www.kantv6.com/%s/%s-' % (sect, tvid)
        debug(t)
        return [(t + '_' + a['part_title'], "https:" + a['url']) for a in dat['data']['partList']]

    def get_title(self, tvid, sect):
        u = "https://www.kantv6.com/index.php/video/info"
        u = "%s?tvid=%s&seo=%s" % (u, tvid, sect)
        dat = self.get_hutf(u)
        dat = json.loads(dat)
        debug(json.dumps(dat, indent=2))
        return dat['data']['title']

    def get_stp(self, url):
        m = re.search("/(tvdrama)/(\d+)-(\d+)", url)
        if m:
            sect, tvid, ptid = m.groups()
            return sect, tvid, ptid
        m = re.search("/(tvdrama|movie)/(\d+)", url)
        sect, tvid = m.groups()
        return sect, tvid, ""

    def test(self, argv):
        mu = self.get_m3u8(argv.url)
        echo(mu)

    def test1(self, argv):
        url = 'https://www.kantv6.com/tvdrama/301948271219001-161948271219033'
        url = 'https://www.kantv6.com/index.php/video/part?tvid=301948271219001'
        url = 'https://www.kantv6.com/index.php/video/info?tvid=301948271219001&seo=tvdrama'
        url = 'https://www.kantv6.com/tvdrama/301948271219001'
        url = 'https://www.kantv6.com/movie/301749570845001'
        url = "https://www.kantv6.com/index.php/video/info?tvid=301749570845001&seo=movie"
        dat = self.get_hutf(url)
        dat = json.loads(dat)
        echo(json.dumps(dat, indent=2))
        echo(dat['data']['title'])
        url = "https://www.kantv6.com/index.php/video/play?tvid=301749570845001&line=1&seo=movie"
        dat = self.get_hutf(url)
        dat = json.loads(dat)
        echo(json.dumps(dat, indent=2))
        #self.get_title(url)
        #l = self.get_playlist(url)
        #echo(json.dumps(l, indent=2))


if __name__ == '__main__':
    start(KANTV6)
