import re
import sys
import zlib
try:
    import http.client as httplib
    import urllib.parse as urlparse
    from urllib.request import HTTPCookieProcessor, ProxyHandler
    from urllib.request import HTTPRedirectHandler, Request
    from urllib.request import build_opener

    def echo(*args):
        sys.stdout.write(" ".join(map(str, args)) + "\n")
except ImportError:
    import httplib
    import urlparse
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
        req = Request(url, headers=self.extra_headers)
        rep = self.opener.open(req)
        hds = rep.info()
        #print(repr(info))
        data = rep.read()
        if hds.get("Content-Encoding") == 'gzip':
            echo("It is gzip")
            html = zlib.decompress(data, zlib.MAX_WBITS | 16)
            return html
        elif hds.get("Content-Encoding") == 'deflate':
            echo("It is deflate")
            #decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
            #return decompressobj.decompress(data) + decompressobj.flush()
            html = zlib.decompress(data, -zlib.MAX_WBITS)   
            return html
        else:
            return data

    def get_kind_size(self, url):
        url_parts = urlparse.urlsplit(url)
        conn = httplib.HTTPConnection(url_parts[1])
        #print url_parts
        q = urlparse.urlunsplit(("", "", url_parts[2], url_parts[3], ""))
        conn.request("HEAD", q)
        resp = conn.getresponse()
        echo(resp.status, resp.reason)
    
        echo("data1 =", resp.read())
        conn.close()
        echo(resp.getheaders())
        size = int(resp.getheader('Content-Length', '0'))
        kind = resp.getheader('Content-Type', '')
        return kind, size

    def get_total_size(self, urllist):
        size = 0
        cnt = 0
        echo("total %d" % len(urllist))
        for url in urllist:
            k, s = self.get_kind_size(url)
            size += s
            cnt += 1
            #sys.stdout.write("%d / %d\r" % (cnt, len(urllist)))
            echo("%d / %d" % (cnt, len(urllist)))
        echo("")
        echo("size =", size)
        return k, size

    def get_total_size_mt(self, urllist, t = 10):
        size = 0
        cnt = 0
        echo("total %d" % len(urllist))
        for url in urllist:
            k, s = self.get_kind_size(url)
            size += s
            cnt += 1
            #sys.stdout.write("%d / %d\r" % (cnt, len(urllist)))
            echo("%d / %d" % (cnt, len(urllist)))
        echo("")
        echo("size =", size)
        return k, size


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
