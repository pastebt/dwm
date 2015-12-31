import re
import sys
import zlib
try:
    from urllib.request import HTTPCookieProcessor, ProxyHandler
    from urllib.request import HTTPRedirectHandler, Request
    from urllib.request import build_opener
    def echo(*args):
        sys.stdout.write(" ".join(map(str, args)) + "\n")
except ImportError:
    from urllib2 import HTTPCookieProcessor, ProxyHandler
    from urllib2 import HTTPRedirectHandler, Request
    from urllib2 import build_opener
    def echo(*args):
        #sys.stdout.write(" ".join(map(str, args)) + "\n")
        for arg in args:
            if isinstance(arg, unicode):
                sys.stdout.write(arg.encode("utf8"))
            else:
                sys.stdout.write(str(arg))
            sys.stdout.write(" ")
        sys.stdout.write("\n")
                

class DWM(object):
    def __init__(self):
        self.redirh = HTTPRedirectHandler()
        self.cookie = HTTPCookieProcessor()
        self.opener = build_opener(self.redirh, self.cookie)
        #self.proxyh = ProxyHandler({'http': "http://211.155.86.25:8888"})
        #self.opener = build_opener(self.proxyh, self.redirh, self.cookie)
        self.extra_headers = {}

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
        for k, v in self.extra_headers.items():
            #print("add header", k, v)
            req.add_header(k, v)
        
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


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns 
       (first-subgroups only).
    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.
    Returns:
        When only one pattern is given, returns a string
        (None if no match found).
        When more than one pattern are given, returns a list of strings
        ([] if no match found).
    """
    #text = str(text)
    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


if __name__ == '__main__':
    d = DWM()
    html = d.get_html("http://www.bilibili.com/video/av2060396/")
    print(html)
    #print(zlib.decompress(open('a.zip', 'rb').read(), -zlib.MAX_WBITS))  # deflate
    #print(zlib.decompress(open('a.zip', 'rb').read(), zlib.MAX_WBITS))   # zlib
    #print(zlib.decompress(open('a.zip', 'rb').read(), zlib.MAX_WBITS|16)) # gzip

    #'http://ws.acgvideo.com/3/af/3190241-1.flv', 'http://ws.acgvideo.com/c/d8/3190242-1.flv'
