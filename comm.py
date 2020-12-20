# -*- coding: utf8 -*-

import os
import re
import ssl
import sys
import zlib
import argparse
import subprocess
from time import sleep

try:
    from queue import Queue
    import http.client as httplib
    import urllib.parse as urlparse
    from urllib.parse import quote
    from urllib.request import HTTPCookieProcessor, ProxyHandler
    from urllib.request import HTTPRedirectHandler, HTTPSHandler
    from urllib.request import Request
    from urllib.request import build_opener
    py3 = True

    def echo(*args):
        sys.stdout.write(" ".join(map(str, args)) + "\n")
        sys.stdout.flush()

    def U(dat):
        return dat
except ImportError:
    import httplib
    import urlparse
    from urllib import quote
    from Queue import Queue
    from urllib2 import HTTPCookieProcessor, ProxyHandler
    from urllib2 import HTTPRedirectHandler, HTTPSHandler
    from urllib2 import Request
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
        sys.stdout.flush()

    def U(dat):
        if not isinstance(dat, unicode):
            return dat.decode('utf8')
        return dat

import ssl

from post import post_file
from merge import merge, tss, m3u8_merge

#USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:33.0) '
#USER_AGENT += 'Gecko/20100101 Firefox/33.0'
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
DEBUG = False
UTITLE = "UnknownTitle"


def debug(*args):
    global DEBUG
    if not DEBUG:
        return
    echo(*args)


class UO(object):
    def __init__(self, url, referer):
        self.url = url
        self.referer = referer


class DWM(object):
    out_dir = './'
    info_only = False
    align_num = 0
    is_playlist = False
    handle_list = []
    get_html_url = ''
    no_proxy = False
    wget_cookie = {}
    no_check_certificate = False
    skim_output = False

    def __init__(self, proxy=None):
        global USER_AGENT
        self.redirh = HTTPRedirectHandler()
        self.cookie = HTTPCookieProcessor()
        self.rawopen = build_opener(self.redirh, self.cookie)
        if proxy is None or self.no_proxy:
            self.opener = self.rawopen
        elif proxy == 'auto':
            # proxy.uku.im:8888
            #self.proxyh = ProxyHandler({'http': "http://211.155.86.25:8888"})
            #self.proxyh = ProxyHandler({'http': "proxy.uku.im:8888"})
            self.proxyh = ProxyHandler({'http': "https://secure.uku.im:8443"})
            #self.proxyh = ProxyHandler({'http': "https://proxy.uku.im:443"})
            self.opener = build_opener(self.proxyh, self.redirh, self.cookie)
        else:
            self.proxyh = ProxyHandler(proxy)
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

    def chrome_hutf(self, url):
        echo("google-chrome wait ...")
        p = subprocess.Popen(["google-chrome", "--headless", "--disable-gpu",
                              "--dump-dom", "--repl", url],
                             stdout=subprocess.PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        debug(hutf)
        return hutf

    def phantom_hutf(self, url, timeout=300, refer=None, postdata=None):
        echo('phantomjs wait', timeout, '...')
        cmd = ["./phantomjs", "dwm.js", str(timeout), url]
        if refer:
            cmd.append(refer)
        if postdata:
            cmd.append(postdata)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        return hutf

    def last_m3u8(self, src):
        us = [src]
        while len(us) == 1:
            last = us[0]
            us = self._get_m3u8_urls(last, self.get_html(last))
            t, s = get_kind_size(us[0])
            if t != 'm3u8':
                break
        return last

    def try_m3u8(self, src):
        #url = 'http://www.ttwanda.com/films/us/2091.html?ac'
        # http://www.ttwanda.com/films/us/1881.html?le  mp2t
        us = self._get_m3u8_urls(src, self.get_html(src))
        if len(us) == 1:
            t, s = get_kind_size(us[0])
            if t == 'm3u8':
                us = self.try_m3u8(us[0])
        return us

    def _get_m3u8_urls(self, src, data):
        bu = os.path.dirname(src) + "/"
        rt = "/".join(src.split('/')[:3])
        urls = []
        for line in data.split('\n'):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "://" in line:
                urls.append(line)
            elif line[0] == '/':
                urls.append(rt + line)
            else:
                urls.append(bu + line)
        return urls

    def get_outfn(self, title, ext, unum=0):
        outfn = of = os.path.join(self.out_dir, title + "." + ext)
        if unum > 1 and ext in tss:
            of = os.path.join(self.out_dir, title + ".mp4")
        if os.path.exists(of):
            echo(of + " exists")
            return None
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        #return outfn
        return of

    def align_title_num(self, t):
        t2 = '-'.join(t.split('/'))
        if self.align_num < 2:
            return t2
        ns = re.split("(\d+)", t2, 1)
        return ("%%s%%0%dd%%s" % self.align_num) % (ns[0], int(ns[1]), ns[2])

    def get_total_size(self, urllist):
        echo("total %d" % len(urllist))
        if len(urllist) > 9:
            k, s = get_total_size_mt(urllist)
        else:
            k, s = get_total_size_st(urllist)
        return k, s

    def use_dwm_merge(self, urls, title, ext, clean=True):
        if self.no_merge:
            echo("skip merge")
            return
        merge(os.path.join(self.out_dir, title), ext, len(urls), clean)

    def download_urls_you_get(self, title, ext, urls, totalsize):
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

    def get_real_url(self, bu, rt, uri):
        if "://" in uri:
            u = uri
        elif uri[0] == '/':
            u = rt + uri
        else:
            u = bu + uri
        return u

    def try_key(self, bu, rt, dn, line):
        m = re.search('#EXT-X-KEY:.+URI="([^"]+)"', line)
        if not m:
            return line
        u = self.get_real_url(bu, rt, m.group(1))
        n = os.path.basename(u)
        self.wget_one_url(os.path.join(dn, n), u, 0)
        return line.replace(m.group(1), n)

    def wget_m3u8(self, title, url):
        dn = os.path.join(self.out_dir, title + ".dwm")
        if not os.path.exists(dn):
            os.makedirs(dn)
        data = self.get_hutf(url)
        fm3u8 = os.path.join(dn, title + ".m3u8")
        fout = open(fm3u8, "w")
        bu = os.path.dirname(url) + "/"
        rt = "/".join(url.split('/')[:3])
        #lines = [l.strip() for l in data.split('\n')]
        #unum = len([l for l in lines if l and l[0] != '#'])
        #echo("unum =", unum)
        #cnt = 0
        dats = []
        for line in data.split('\n'):
            if not line or line.startswith("#"):
                line = self.try_key(bu, rt, dn, line)
                fout.write(line + "\n")
                #fout.flush()
                continue
            u = self.get_real_url(bu, rt, line)
            n = os.path.basename(u)
            fout.write(n + "\n")
            dats.append((os.path.join(dn, n), u))
            #fout.flush()
            #cnt += 1
            #echo("progress = %.1f%%" % (100.0 * cnt / unum))
            #self.wget_one_url(os.path.join(dn, n), u, unum)
        fout.write("#%s\n" % url)
        fout.close()
        cnt = 0
        unum = len(dats)
        echo("unum =", unum)
        for t, u in dats:
            ret = self.wget_one_url(t, u, unum)
            if ret == 0:
                cnt += 1
                echo("progress = %.1f%%" % (100.0 * cnt / unum))
        if cnt == unum:
            echo("progress = 100%")
            echo("merge")
            self.avconv_m3u8(title, "mp4", fm3u8)
        else:
            echo("some download failed %d != %d, skip merge" % (cnt, unum))

    def download_m3u8(self, title, url):
        outfn = self.get_outfn(title, "mp4")
        if not outfn:
            return    # file exists
        echo("download", outfn)
        #if self.skim_output:
        #    self.wget_m3u8(title, url)
        #else:
        #    self.avconv_m3u8(title, "mp4", url)
        if self.parsed_args.avconv_m3u8:
            self.avconv_m3u8(title, "mp4", url)
        else:
            self.wget_m3u8(title, url)
        return outfn

    def avconv_m3u8(self, title, ext, url):
        outfn = self.get_outfn(title, ext)
        m3u8_merge(url, outfn)
        ##if not title.endswith(".mp4"):
        ##    title += ".mp4"
        #cmds = ["avconv",
        #        "-allowed_extensions", "ALL",
        #        "-i", url,
        #        "-acodec", "copy",
        #        "-vcodec", "copy",
        #        "-f", "mp4",
        #        outfn + ".dwm",
        #        ]
        #debug(cmds)
        #p = subprocess.Popen(cmds, env={"LANG": "en_CA.UTF-8"})
        #p.wait()
        #if p.returncode == 0:
        #    os.rename(outfn + ".dwm", outfn)
        #    echo(outfn)

    def wget_urls(self, title, ext, urls, tsize):
        if ext is None:
            k, s = get_kind_size(urls[0])
            ext = k
        #echo("ext=%s, tsize=%d" % (ext, tsize))
        title = "_".join(title.split('/'))
        unum = len(urls)
        outfn = self.get_outfn(title, ext, unum)
        if not outfn:
            return    # file exists
        echo("download", outfn)
        if unum == 1:
            return self.wget_one_url(outfn, urls[0], 1, tsize)
        #for cnt, url in enumerate(urls[self.dwn_skip:], start=self.dwn_skip):
        for cnt, url in enumerate(urls):
            echo("progress = %.1f%%" % (100.0 * cnt / len(urls)))
            outfn = self.get_outfn("%s[%02d]" % (title, cnt), ext)
            if outfn:
                self.wget_one_url(outfn, url, unum)
        echo("progress = 100%")
        self.use_dwm_merge(urls, title, ext, False)
        return outfn

    def wget_one_url(self, outfn, url, unum, totalsize=0):
        if unum > 1:
            echo("wget", outfn, "/", unum)
        else:
            echo("wget", outfn)
        dwnfn = outfn + ".dwm"
        cmds = ["wget",
                "-U", USER_AGENT,
                #"--wait", "10",
                #"--tries=50",
                #"--read-timeout=60",
                "--timeout=60",
                "--continue",
                "--no-use-server-timestamps",
                #"-S",
                #"--no-verbose",
                ]

        if self.skim_output:
            cmds.append("--quiet")
            #cmds.append("--show-progress")
            #cmds.append("--progress=bar:force")

        if self.no_check_certificate:
            cmds.append("--no-check-certificate")

        # --header='Cookie: FTN5K=af45f935;'
        if self.wget_cookie:
            cmds.append("--header=Cookie: " + self.wget_cookie)

        if isinstance(url, UO):
            cmds += ["-O", dwnfn, "--header=Referer: " + url.referer, url.url]
        else:
            cmds += ["-O", dwnfn, url]
        debug(cmds)
        for i in range(10):
            p = subprocess.Popen(cmds, env={"LANG": "en_CA.UTF-8"})
            if self.skim_output and totalsize > 0:
                p.poll()
                while p.returncode is None:
                    if os.path.exists(dwnfn):
                        echo("progress = %.1f%%" % (
                              100.0 * os.stat(dwnfn).st_size / totalsize))
                    sleep(2)
                    p.poll()
            else:
                p.wait()

            if p.returncode == 0:
                os.rename(dwnfn, outfn)
                break
            sleep(1 + i)
        return p.returncode

    #def get_one(self, url, t="UnknownTitle", n=False):
    def get_one(self, url, t=UTITLE, n=False):
        title, ext, urls, size = self.query_info(url)
        debug("get_one from query_info title=", title)
        if not urls:
            echo("Empty urls")
            return
        if not title or t != UTITLE:
            if ext and title.endswith("." + ext):
                title = t[:-len("." + ext)]
            else:
                title = t
        nt = norm_title(title)
        debug("norm_title return", nt)
        if n:
            title = nt
        else:
            echo('nt =', nt)
        if self.info_only:
            for url in urls:
                echo(url)
        title = self.align_title_num(title)
        if self.info_only or len(urls) == 1:
            if ext is None or size is None:
                e, s = self.get_total_size(urls)
                if ext is None:
                    ext = e
                if size is None:
                    size = s
            echo("title =", title, ext)
            echo("Size:\t%.2f MiB (%d Bytes)" % (round(size / 1048576.0, 2),
                                                 size))
        if self.info_only:
            return

        if ext == 'm3u8':
            outfn = self.download_m3u8(title, urls)
        else:
            outfn = self.download_urls(title, ext, urls, size)
        if self.parsed_args.post_uri and outfn:
            #post_file(outfn.encode('utf8'), self.parsed_args.post_uri)
            post_file(outfn, self.parsed_args.post_uri)

    def try_playlist(self, ispl, url):
        if ispl:
            urls = self.get_playlist(url)
            for t, u in urls:
                debug(t, u)
            return urls
        return None

    def get_playlist(self, page_url):
        #raise Exception("Not Implement Yet")
        echo("Playlist Not Implement")
        return []

    def clean_up(self):
        pass

    def test(self, args):
        echo("test Not Implement")

    @classmethod
    def can_handle_it(cls, url):
        for h in cls.handle_list:
            #if h in url:
            if re.search(h, url):
                return True
        return False


def get_kind_size(u, cookie=""):
    kinds = {}
    if isinstance(u, UO):
        url = u.url
        ref = u.referer
    else:
        url = u
        ref = ""
    act = 'HEAD'
    while url:
        debug('get_kind_size, url =', url)
        url_parts = urlparse.urlsplit(url)
        if url_parts[0] == 'https':
            conn = httplib.HTTPSConnection(url_parts[1],
                                context=ssl._create_unverified_context())
        else:
            conn = httplib.HTTPConnection(url_parts[1])
        # print url_parts
        q = urlparse.urlunsplit(("", "", url_parts[2], url_parts[3], ""))
        hd = {'User-Agent': USER_AGENT}
        if cookie:
            hd['Cookie'] = cookie
        if ref:
            hd['Referer'] = ref
        debug(hd)
        conn.request(act, q, "", hd)
        try:
            resp = conn.getresponse()
        except httplib.BadStatusLine:   # some not know HEAD
            conn.close()
            act = "GET"
            conn.request("GET", q, "", hd)
            resp = conn.getresponse()
        conn.close()
        debug(resp.status, resp.reason)
        if resp.status == 404 and act != "GET":
            # http://server3.dnvod.tv/hvod/lxj-tscgwlb-50-022061041.mp4
            act = "GET"
            continue
        debug(resp.getheaders())
        url = resp.getheader('Location', '')
        if not url:
            size = int(resp.getheader('Content-Length', '0'))
            kind = resp.getheader('Content-Type', '')
            # application/vnd.apple.mpegURL
            # application/x-mpegURL
            if kind.lower().endswith(".mpegurl") or kind.lower().endswith('/x-mpegurl'):
                return "m3u8", size
            if not size:
                url = u
                act = 'GET'
    kind = resp.getheader('Content-Type', '')
    debug('Content-Type:', kind)
    for k in kind.split(';'):
        if 'video' in k:
            kind = k.split('/')[-1]
        if k == 'application/octet-stream':
            kind = 'ts'
    return kinds.get(kind, kind), size


def get_total_size_st(urllist):
    size = 0
    cnt = 0
    k = "ext"
    for url in urllist:
        k, s = get_kind_size(url)
        size += s
        cnt += 1
        debug("%d / %d = %d" % (cnt, len(urllist), s))
    echo("")
    return k, size


def get_total_size_mt(urllist, tn=10):
    from threading import Thread
    qsrc, qdst = Queue(), Queue()
    size = 0
    cnt = 0

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


numap = {}
cnum = U("一二三四五六七八九十")
sere = "([" + cnum + U("]+)季")
epre = "([" + cnum + U("]+)集")
npre = U("(\d+)集")


def c2n(cs):
    n = 0
    for c in cs:
        i = numap[c]
        if i < 10:
            n = n + i
        elif n:
            n = n * 10
        else:
            n = 10
    return n


def norm_title(title):
    global numap
    for i, c in enumerate(cnum, 1):
        numap[c] = i
    debug(title)
    m = re.search("(s\d{1,2}e\d{1,2})[\.\s]*", title, flags=re.I + re.U)
    if m:
        g = m.groups()
        return g[0].upper() + '_' + title[:m.start()] + title[m.end():]
    se = ""
    m = re.search(sere, title)
    if m:
        debug(m.group(1))
        se = "S%02d" % c2n(m.group(1))
    m = re.search(epre, title)
    if m:
        debug(m.group(1))
        se = se + "E%02d" % c2n(m.group(1))
    elif se:    # already has S0X
        m = re.search(npre, title, re.U)
        if m:
            se = se + "E%02d" % int(m.group(1))
    if se:
        se = se + "_"
    return se + title


def start(kls):
    global DEBUG
    p = argparse.ArgumentParser(description='Download Web Movie')
    #, add_help=False)
    p.add_argument('url', metavar='URL', type=str, action='store',
                   help='url of movie')
    p.add_argument('-i', '--info_only', action='store_true',
                   help='show information only')
    p.add_argument('-o', '--output', metavar='dir', action='store',
                   #help='where download file go, dir or url to post',
                   help='where download file go, dir',
                   default='.')
    p.add_argument('-n', '--norm_title', action='store_true',
                   help='normalize title')
    p.add_argument('-p', '--playlist_only', action='store_true',
                   help='try playlist only')
    p.add_argument('-P', '--not_playlist', action='store_true',
                   help='not try playlist')
    p.add_argument('--playlist_top', type=int, metavar='#', action='store',
                   help='only get top # of playlist', default=0)
    p.add_argument('--playlist_skip', type=int, metavar='#', action='store',
                   help='skip # in playlist', default=0)
    p.add_argument('--title', metavar='TITLE', action='store',
                   help='movie name if you want to define it',
                   default=UTITLE)
    p.add_argument('--post_uri', metavar='URI', action='store',
                   help='uri to post downloaded file')
    #p.add_argument('--wget_skip', type=int, metavar='#', action='store',
    #               help='wget skip # urls in list', default=0)
    p.add_argument('--align_num', type=int, metavar='#', action='store',
                   help='align number', default=0)
    p.add_argument('--cookie', metavar='COOKIE_STR', action='store',
                   help='input cookie for login', default='')
    p.add_argument('--user_agent', metavar='USER_AGENT', action='store',
                   help='pair with cookie for login', default='')
    p.add_argument('--no_merge', action='store_true',
                   help='skip merge video pieces')
    p.add_argument('--no_check_certificate', action='store_true',
                   help='not check https certificate')
    p.add_argument('--no_proxy', action='store_true',
                   help='disable auto proxy')
    p.add_argument('--skim_output', action='store_true',
                   help='only output data for WUI')
    p.add_argument('--avconv_m3u8', action='store_true',
                   help='download m3u8 by avconv')
    p.add_argument('--debug', action='store_true',
                   help='display debug message')
    p.add_argument('--testing', action='store_true',
                   help='do testing')
    args = p.parse_args()
    DEBUG = args.debug
    debug(args)

    if not getattr(kls, 'query_info', None):
        kls = kls(args.url)
        if kls is None:
            echo("Not support ", args.url)
            sys.exit(1)
    if args.title == "":
        args.title = UTITLE
    if py3:
        kls.title = args.title
    else:
        kls.title = args.title.decode('utf8')
    kls.out_dir = args.output
    kls.no_merge = args.no_merge
    kls.no_proxy = args.no_proxy
    kls.info_only = args.info_only
    kls.align_num = args.align_num
    kls.login_cookie = args.cookie
    kls.login_agent = args.user_agent
    kls.no_check_certificate = args.no_check_certificate
    if args.no_check_certificate:
        ssl._create_default_https_context = ssl._create_unverified_context
    kls.download_urls = DWM.wget_urls
    kls.skim_output = args.skim_output
    k = kls()
    k.parsed_args = args
    if args.testing:
        DEBUG = True
        k.test(args)
    else:
        run(k, args)


def run(k, args):
    pl = k.try_playlist(not args.not_playlist, args.url)
    if pl:
        debug(args.url)
        k.is_playlist = True
        cnt = 0
        for title, url in pl:   # k.get_list(args.url):
            cnt = cnt + 1
            if cnt > args.playlist_top > 0:
                break
            if cnt <= args.playlist_skip:
                continue
            echo(title, url)
            try:
                k.get_one(url, title, args.norm_title)
            except Exception as e:
                #if args.continue_next:
                if args.debug:
                    echo("Error:", e)
                    with open("exception_%s.txt" % quote(url), "w") as fo:
                        fo.write(title + "\n")
                        fo.write(url + "\n")
                else:
                    raise
    elif not args.playlist_only:
        k.get_one(args.url, k.title, args.norm_title)
    k.clean_up()


if __name__ == '__main__':
    #d = DWM()
    #html = d.get_html("http://www.bilibili.com/video/av2060396/")
    #print(html)
    #start(DWM)
    echo(norm_title("abc S01e02.qwe"))
    echo(norm_title("abcS01e02.  qwe"))
    echo(norm_title(U("测试 第一季 第五集")))
    echo(norm_title(U("测试 第一季 第十集")))
    echo(norm_title(U("测试 第一季 第十五集")))
    echo(norm_title(U("测试 第一季 第一十五集")))
    echo(norm_title(U("测试 第一季 第二十五集")))
    echo(norm_title(U("测试 第一季 第12集")))
