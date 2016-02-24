#! /usr/bin/pyhton

import os
import sys
from httplib import HTTPConnection


class UpFile(object):
    def __init__(self, filename, name, bun=""):
        self.s = 0
        self.f = open(filename)
        pre = "--%s\r\n" % bun
        pre = '%sContent-Disposition: form-data; name="%s"' % (pre, name)
        pre = '%s; filename="%s"\r\n' % (pre, os.path.basename(filename))
        pre = '%sContent-Type: text/plain\r\n\r\n' % pre
        self.pre = pre
        self.end = "\r\n--%s--" % bun

    def size(self):
        l = os.fstat(self.f.fileno()).st_size
        return len(self.pre) + l + len(self.end)

    def read(self, bufsize):
        #FIXME, if bufsize < len(self.pre) or bufsize < len(self.end)
        if self.s == 0:
            self.s = 1
            print '#',
            return self.pre
        if self.s == 1:
            buf = self.f.read(bufsize)
            if buf:
                print '#',
                return buf
            self.s = 2
            return self.end
        return ""


def post(fn):
    conn = HTTPConnection("127.0.0.1", 8080)
    bun = "-----------------1212313----61b3e9bf8df4ee45---------------"
    fo = UpFile(fn, 'attachment', bun)
    headers = {"Content-Type": "multipart/form-data; boundary=%s" % bun,
               "Content-Length": str(fo.size())
             }
    conn.request("POST", "/", fo, headers)
    resp = conn.getresponse()
    print
    print resp.status, resp.reason


post(sys.argv[1])
