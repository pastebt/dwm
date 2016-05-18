#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from subprocess import Popen, PIPE
from html.parser import HTMLParser

from comm import DWM, match1, echo, start


class IQIYI(DWM):
    def query_info(self, url):
        # title, ext, urls, totalsize
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
        echo(m.urllist)
        return []


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
