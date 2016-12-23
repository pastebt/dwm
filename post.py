#! /usr/bin/python -B

import os
import re
import sys
try:
    from httplib import HTTPConnection
    from urllib import quote, unquote
    from urlparse import urlparse
    py3 = False
except ImportError:
    from http.client import HTTPConnection
    from urllib.parse import quote, unquote, urlparse
    py3 = True

from comm import echo


class UpFile(object):
    def __init__(self, filename, name, bun=""):
        global py3

        self.s = 0
        self.f = open(filename, "r+b")
        #fn = '_'.join(os.path.basename(filename).split('"'))
        fn = os.path.basename(filename)
        fn = "_".join(re.split('''\?|\:|\|''', fn))
        fn = "'".join(re.split('"', fn))
        pre = "--%s\r\n" % bun
        pre = '%sContent-Disposition: form-data; name="%s"' % (pre, name)
        pre = '%s; filename="%s"\r\n' % (pre, fn)
        pre = '%sContent-Type: text/plain\r\n\r\n' % pre
        if py3:
            self.pre = pre.encode("utf8")
        else:
            self.pre = pre
        self.end = ("\r\n--%s--" % bun).encode("ascii")
        self.tal = 0
        self.cnt = 0

    def size(self):
        self.tal = os.fstat(self.f.fileno()).st_size
        return len(self.pre) + self.tal + len(self.end)

    def read(self, bufsize):
        #FIXME, if bufsize < len(self.pre) or bufsize < len(self.end)
        if self.s == 0:
            self.s = 1
            #print '#',
            return self.pre
        if self.s == 1:
            buf = self.f.read(bufsize)
            if buf:
                #print '#',
                self.cnt += len(buf)
                sys.stdout.write("\r%0.1f" % (self.cnt * 100.0 / self.tal))
                return buf
            self.s = 2
            echo("")
            return self.end
        return ""


def make_host_port(url):
    res = urlparse(url)
    nl = res.netloc
    if not nl:
        return "10.0.0.7", 8080, url
    nls = nl.split(":")
    h = nls[0]
    if len(nls) > 1:
        p = int(nls[1])
    else:
        p = 80
    #conn = HTTPConnection(h, p)
    return h, p, res.path


def get(conn, dst):
    #conn = HTTPConnection("10.0.0.7", 8080)
    echo(repr(dst))
    conn.request("GET", dst)
    resp = conn.getresponse()
    echo(resp.read().decode('utf8'))


def post(h, p, dst, fns):
    for fn in fns:
        conn = HTTPConnection(h, p)
        post_one(fn, conn, dst)


def post_one(fn, conn, dst):
    echo(fn)
    #conn = HTTPConnection(ip, port)
    bun = "-----------------12123135---61b3e9bf8df4ee45---------------"
    fo = UpFile(fn, 'attachment', bun)
    headers = {"Content-Type": "multipart/form-data; boundary=%s" % bun,
               "Content-Length": str(fo.size())
             }
    conn.request("POST", dst, fo, headers)
    resp = conn.getresponse()
    #print
    echo(resp.status, resp.reason)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        echo('Usage:', sys.argv[0], 'remote_path [filename ...]')
        sys.exit(1)
    h, p, dst = make_host_port(sys.argv[1])
    dst = quote(unquote(dst))
    if len(sys.argv) < 3:
        conn = HTTPConnection(h, p)
        get(conn, dst + "?who=cmd")
    else:
        post(h, p, dst + "?who=poster", sys.argv[2:])
