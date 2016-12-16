# -*- coding: utf8 -*-

import os
import re
import sys
import zlib
import argparse
import subprocess
from time import sleep

try:
    from queue import Queue
    import http.client as httplib
    import urllib.parse as urlparse
    from urllib.request import HTTPCookieProcessor, ProxyHandler
    from urllib.request import HTTPRedirectHandler, Request
    from urllib.request import build_opener
    py3 = True

    def echo(*args):
        sys.stdout.write(" ".join(map(str, args)) + "\n")
except ImportError:
    import httplib
    import urlparse
    from Queue import Queue
    from urllib2 import HTTPCookieProcessor, ProxyHandler
    from urllib2 import HTTPRedirectHandler, Request
    from urllib2 import build_opener
    py3 = False

    class ConnectionResetError(Exception):
        pass

    def echo(*args):
        # sys.stdout.write(" ".join(map(str, args)) + "\n")
        for arg in args:
            if isinstance(arg, unicode):
                sys.stdout.write(arg.encode("utf8"))
            elif isinstance(arg, Exception):
                sys.stdout.write(unicode(arg).encode("utf8"))
            else:
                sys.stdout.write(str(arg))
            sys.stdout.write(" ")
        sys.stdout.write("\n")


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:33.0) '
USER_AGENT += 'Gecko/20100101 Firefox/33.0'
DEBUG = False


def debug(*args):
    global DEBUG
    if not DEBUG:
        return
    echo(*args)    


class DWM(object):
    class ExistsError(Exception):
        pass

    out_dir = './'
    info_only = False
    align_num = 0
    dwn_skip = None
    is_playlist = False
    get_html_url = ''

    def __init__(self, proxy=None):
        global USER_AGENT
        self.redirh = HTTPRedirectHandler()
        self.cookie = HTTPCookieProcessor()
        self.rawopen = build_opener(self.redirh, self.cookie)
        if proxy is None:
            self.opener = self.rawopen
        elif proxy == 'auto':
            # proxy.uku.im:8888
            #self.proxyh = ProxyHandler({'http': "http://211.155.86.25:8888"})
            #self.proxyh = ProxyHandler({'http': "proxy.uku.im:8888"})
            self.proxyh = ProxyHandler({'http': "https://secure.uku.im:8443"})
            self.opener = build_opener(self.proxyh, self.redirh, self.cookie)
        self.extra_headers = {"User-Agent": USER_AGENT}

    def get_html(self, url, raw=False, postdata=None):
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
        if raw:
            rep = self.rawopen.open(req, postdata)
        else:
            rep = self.opener.open(req, postdata)
        self.get_html_url = rep.geturl()
        hds = rep.info()
        # print(repr(info))
        data = rep.read()
        if hds.get("Content-Encoding") == 'gzip':
            echo("It is gzip")
            html = zlib.decompress(data, zlib.MAX_WBITS | 16)
            return html
        elif hds.get("Content-Encoding") == 'deflate':
            echo("It is deflate")
            # decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
            # return decompressobj.decompress(data) + decompressobj.flush()
            html = zlib.decompress(data, -zlib.MAX_WBITS)
            return html
        else:
            return data

    def get_hutf(self, *param, **dd):
        return self.get_html(*param, **dd).decode('utf8', 'ignore')

    def check_exists(self, title, ext):
        if self.info_only:
            return
        outfn = os.path.join(self.out_dir, title + "." + ext)
        if os.path.exists(outfn):
            raise self.ExistsError(outfn + " exists")

    def align_title_num(self, t):
        t2 = '-'.join(t.split('/'))
        if self.align_num < 2:
            return t2
        ns = re.split("(\d+)", t2, 1)
        return ("%%s%%0%dd%%s" % self.align_num) % (ns[0], int(ns[1]), ns[2])

    def get_total_size(self, urllist):
        if len(urllist) > 9:
            k, s = get_total_size_mt(urllist)
        else:
            k, s = get_total_size_st(urllist)
        echo("Size:\t%.2f MiB (%d Bytes)" % (round(s / 1048576.0, 2), s))
        return k, s

    def use_dwm_merge(self, urls, title, ext, clean=True):
        from merge import merge
        merge(os.path.join(self.out_dir, title), ext, len(urls), clean)

    def download_urls(self, title, ext, urls, totalsize):
        sys.path.insert(1, '../you-get/src')
        from you_get.common import download_urls
        try:
            download_urls(urls, title, ext, totalsize, self.out_dir)
        except subprocess.CalledProcessError as sc:
            if "avconv" not in str(sc):
                raise sc
            # failed to merge because avconv disable concat protocol
            #from merge import merge
            #merge(os.path.join(self.out_dir, title), ext, len(urls), True)
            echo("")
            self.use_dwm_merge(urls, title, ext)
        except RuntimeError as r:
            if "reraise" not in str(r):
                raise r
            self.use_dwm_merge(urls, title, ext)

    def wget_urls(self, title, ext, urls, tsize):
        title = "_".join(title.split('/'))
        if len(urls) == 1:
            self.wget_one_url(title, ext, urls[0], 1)
            return
        cnt = 0
        for url in urls:
            if cnt >= self.dwn_skip:
                self.wget_one_url("%s[%02d]" % (title, cnt),
                                  ext, url, len(urls))
            cnt = cnt + 1
        self.use_dwm_merge(urls, title, ext, False)

    def wget_one_url(self, title, ext, url, unum):
        outfn = os.path.join(self.out_dir, title + "." + ext)
        if os.path.exists(outfn):
            echo("skip", outfn)
            return
        else:
            echo("download", outfn, "/", unum)
            dwnfn = outfn + ".dwm"
            p = subprocess.Popen(["wget", 
                                  "-U", USER_AGENT,
                                  #"--wait", "30",
                                  #"--tries=50",
                                  "--read-timeout=30",
                                  "-c",
                                  "--no-use-server-timestamps",
                                  #"-S", 
                                  "-O", dwnfn,
                                  url])
            p.wait()
            #if os.stat(dwnfn).st_size == totalsize:
            if p.returncode == 0:
                os.rename(dwnfn, outfn)

    def get_one(self, url, t="UnknownTitle"):
        try:
            title, ext, urls, size = self.query_info(url)
        except self.ExistsError as e:
            echo(e)
            return
        if not urls:
            echo("Empty urls")
            return
        if not title:
            title = t
        if self.info_only:
            if ext is None or size is None:
                e, s = self.get_total_size(urls)
                if ext is None:
                    ext = e
                if size is None:
                    size = s
            for url in urls:
                echo(url)
            echo("title =", title, ext)
            echo("Size:\t%.2f MiB (%d Bytes)" % (
                  round(size / 1048576.0, 2), size))
        else:
            self.download_urls(title, ext, urls, size)

    def try_playlist(self, ispl, url):
        if ispl:
            return self.get_list(url)
        return None

    def get_list(self, page_url):
        raise Exception("Not Implement Yet")
    
    def clean_up(self):
        pass


def get_kind_size(u):
    url = u
    while url:
        debug('get_kind_size, url =', url)
        url_parts = urlparse.urlsplit(url)
        if url_parts[0] == 'https':
            conn = httplib.HTTPSConnection(url_parts[1])
        else:
            conn = httplib.HTTPConnection(url_parts[1])
        # print url_parts
        q = urlparse.urlunsplit(("", "", url_parts[2], url_parts[3], ""))
        #print h
        conn.request("HEAD", q) #, "", h)
        #conn.request("GET", q) #, "", h)
        resp = conn.getresponse()
        #echo("data1 =", resp.read())
        conn.close()
        #echo(resp.getheaders())
        #echo(resp.status, resp.reason)
        #if resp.status == 302:
        url = resp.getheader('Location', '')
    size = int(resp.getheader('Content-Length', '0'))
    kind = resp.getheader('Content-Type', '') #.split("-")[1]
    return kind, size


def get_total_size_st(urllist):
    size = 0
    cnt = 0
    k = "ext"
    echo("total %d" % len(urllist))
    for url in urllist:
        k, s = get_kind_size(url)
        size += s
        cnt += 1
        sys.stdout.write("%d / %d\r" % (cnt, len(urllist)))
        # echo("%d / %d" % (cnt, len(urllist)))
    echo("")
    # echo("size =", size)
    return k, size


def get_total_size_mt(urllist, tn=10):
    from threading import Thread
    qsrc, qdst = Queue(), Queue()
    size = 0
    cnt = 0
    echo("total %d" % len(urllist))

    def worker():
        while True:
            url = qsrc.get()
            if not url:
                break
            k, s = get_kind_size(url)
            qdst.put((k, s))

    ths = []
    for i in range(tn):
        th = Thread(target=worker)
        ths.append(th)
        th.start()

    for url in urllist:
        qsrc.put(url)
    for i in range(tn):
        qsrc.put("")
    for th in ths:
        th.join()

    for url in urllist:
        k, s = qdst.get(False)
        size += s
        cnt += 1
        # sys.stdout.write("%d / %d\r" % (cnt, len(urllist)))
        # echo("%d / %d" % (cnt, len(urllist)))
    # echo("")
    # echo("size =", size, "cnt =", cnt)
    return k, size


def search_first(text, *patterns):
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match
    return None


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


def start(kls):
    global DEBUG
    p = argparse.ArgumentParser(description='Download Web Movie')
    #, add_help=False)
    p.add_argument('url', metavar='URL', type=str, action='store',
                   help='url of movie')
    #p.add_argument('-p', '--playlist', action='store_true',
    #               help='url is playlist or not')
    p.add_argument('-i', '--info_only', action='store_true',
                   help='show information only')
    p.add_argument('-a', '--align_num', type=int, metavar='#', action='store',
                   help='align number', default=0)
    p.add_argument('--playlist_top', type=int, metavar='#', action='store',
                   help='only get top # of playlist', default=0)
    p.add_argument('--playlist_skip', type=int, metavar='#', action='store',
                   help='skip # in playlist', default=-1)
    p.add_argument('--wget_skip', type=int, metavar='#', action='store',
                   help='wget skip # urls in list', default=0)
    p.add_argument('-o', '--output', metavar='dir|url', action='store',
                   help='where download file go, dir or url to post',
                   default='.')
    p.add_argument('-t', '--title', metavar='TITLE', action='store',
                   help='movie name if you want to define it',
                   default='Unknown')
    p.add_argument('--debug', action='store_true',
                   help='display debug message')
    args = p.parse_args()
    DEBUG = args.debug
    debug(args)
    kls.title = args.title
    kls.out_dir = args.output
    kls.info_only = args.info_only
    kls.align_num = args.align_num
    if args.wget_skip >= 0:
        kls.download_urls = DWM.wget_urls
        kls.dwn_skip = args.wget_skip
    elif not py3 and not kls.info_only:
        raise Exception("you need py3 while using you-get download, or you can set --wget_skip 0")
    k = kls()
    if args.playlist_skip == -2:
        pl = None
    else:
        pl = k.try_playlist(args.playlist_skip >= 0 or args.playlist_top > 0,
                        args.url)
    if pl:
        echo(args.url)
        k.is_playlist = True
        cnt = 0
        for title, url in pl: #k.get_list(args.url):
            cnt = cnt + 1
            if cnt > args.playlist_top > 0:
                break
            if cnt < args.playlist_skip:
                continue
            echo(title, url)
            for i in range(2):
                try:
                    k.get_one(url, title)
                except subprocess.CalledProcessError as e:
                    echo(e)
                    return
                #except Exception as e:
                #    echo(type(e), e, "will try again ...")
                #    sleep(5)
                #    continue
                else:
                    break
    else:
        k.get_one(args.url)
    k.clean_up()


if __name__ == '__main__':
    #d = DWM()
    #html = d.get_html("http://www.bilibili.com/video/av2060396/")
    #print(html)
    start(DWM)
