import sys

from urllib.request import HTTPCookieProcessor, ProxyHandler
from urllib.request import HTTPRedirectHandler, Request
from urllib.request import build_opener


class DWM(object):
    def __init__(self):
        #self.proxyh = ProxyHandler("http", "211.155.86.25:8888")
        self.redirh = HTTPRedirectHandler()
        self.cookie = HTTPCookieProcessor()
        self.opener = build_opener(self.redirh, self.cookie)

    def get_html(self, url):
        req = Request(url)
        rep = self.opener.open(req)
        #print(rep.info())
        print(rep.read())

d = DWM()
d.get_html("http://www.bilibili.com/video/av2060396/")

