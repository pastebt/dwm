#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from subprocess import Popen, PIPE
from html.parser import HTMLParser

from comm import DWM, match1, echo, start


class IQIYI(DWM):
    def query_info(self, url):
        # title, ext, urls, totalsize
        sys.path.insert(1, '../you-get/src')
        from you_get.extractors.iqiyi import Iqiyi
        i = Iqiyi(url)
        i.prepare()
        #echo(i.stream_urls)

        #try:
        i.streams_sorted = [dict([('id', stream_type['id'])] + list(i.streams[stream_type['id']].items())) for stream_type in Iqiyi.stream_types if stream_type['id'] in i.streams]
        #except:
        #    i.streams_sorted = [dict([('itag', stream_type['itag'])] + list(i.streams[stream_type['itag']].items())) for stream_type in i.__class__.stream_types if stream_type['itag'] in i.streams]
        #echo(i.streams_sorted)
        i.extract()
        echo(i.streams_sorted)
        echo(i.streams)
        return

    def get_list(self, page_url):
        p = Popen(["./phantomjs", "dwm.js", "600", page_url], stdout=PIPE)
        html = p.stdout.read()
        p.wait()
        #html = self.get_html(page_url)
        #echo(html)
        hutf = html.decode("utf8")
        #echo(hutf)
        c = hutf.split("<!--视频列表区域 -->")[1]
        m = MyHTMLParser("")
        m.feed(c)
        #echo(m.urllist)
        return m.urllist


class MyHTMLParser(HTMLParser):
    def __init__(self, name):
        HTMLParser.__init__(self)
        self.name = name
        self.urllist = []
        self.u = ""
        self.e = ""
        self.d = ""

    def handle_starttag(self, tag, attrs):
        # http://www.iqiyi.com/a_19rrhb9eet.html 太阳的后裔
        if tag == "em":
            self.e = "em"
            return
        if tag != 'a':
            return
        ats = dict(attrs)
        if ats.get("data-elem") != "itemlink":
            return
        self.u = ats.get('href')

    def handle_endtag(self, tag):
        if tag == 'a':
            self.u = ""
        if tag == 'em':
            if self.u and self.d:
                self.urllist.append((self.d, self.u))
            self.e = ""
            self.d = ""

    def handle_data(self, data):
        if self.e and self.u:
            self.d = self.d + data


if __name__ == '__main__':
    start(IQIYI)
