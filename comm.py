import sys
import zlib
try:
    from urllib.request import HTTPCookieProcessor, ProxyHandler
    from urllib.request import HTTPRedirectHandler, Request
    from urllib.request import build_opener
except ImportError:
    from urllib2 import HTTPCookieProcessor, ProxyHandler
    from urllib2 import HTTPRedirectHandler, Request
    from urllib2 import build_opener
    

class DWM(object):
    def __init__(self):
        self.redirh = HTTPRedirectHandler()
        self.cookie = HTTPCookieProcessor()
        self.opener = build_opener(self.redirh, self.cookie)
        #self.proxyh = ProxyHandler({'http': "http://211.155.86.25:8888"})
        #self.opener = build_opener(self.proxyh, self.redirh, self.cookie)

    def get_html(self, url):
        '''
        Date: Mon, 13 Apr 2015 05:35:05 GMT
        Content-Type: text/html
        Transfer-Encoding: chunked
        Connection: close
        Server: Tengine
        Content-Encoding: gzip
        X-Cache: HIT from us-newyork-ubi.hdslb.com
        '''
        req = Request(url)
        rep = self.opener.open(req)
        hds = rep.info()
        #print(repr(info))
        data = rep.read()
        if hds.get("Content-Encoding") == 'gzip':
            print("It is gzip")
            html = zlib.decompress(data, zlib.MAX_WBITS|16)
            return html
        else:
            return data

d = DWM()
html = d.get_html("http://www.bilibili.com/video/av2060396/")
print(html)
#print(zlib.decompress(open('a.zip', 'rb').read(), -zlib.MAX_WBITS))  # deflate
#print(zlib.decompress(open('a.zip', 'rb').read(), zlib.MAX_WBITS))   # zlib
#print(zlib.decompress(open('a.zip', 'rb').read(), zlib.MAX_WBITS|16)) # gzip

#'http://ws.acgvideo.com/3/af/3190241-1.flv', 'http://ws.acgvideo.com/c/d8/3190242-1.flv'
