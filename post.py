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
        self.tal = 0
        self.cnt = 0

    def size(self):
        self.tal = os.fstat(self.f.fileno()).st_size
        return len(self.pre) + self.tal + len(self.end)

    def read(self, bufsize):
        #FIXME, if bufsize < len(self.pre) or bufsize < len(self.end)
        if self.s == 0:
            self.s = 1
            print '#',
            return self.pre
        if self.s == 1:
            buf = self.f.read(bufsize)
            if buf:
                #print '#',
                self.cnt += len(buf)
                sys.stdout.write("%0.1f\r" % (self.cnt * 100.0 / self.tal))
                return buf
            self.s = 2
            print ""
            return self.end
        return ""


def post(fn, dst):
    conn = HTTPConnection("10.0.0.7", 8080)
    bun = "-----------------1212313----61b3e9bf8df4ee45---------------"
    fo = UpFile(fn, 'attachment', bun)
    headers = {"Content-Type": "multipart/form-data; boundary=%s" % bun,
               "Content-Length": str(fo.size())
             }
    conn.request("POST", dst, fo, headers)
    resp = conn.getresponse()
    #print
    print resp.status, resp.reason


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:', sys.argv[0], 'filename  remote_path'
        sys.exit(1)
    post(sys.argv[1], sys.argv[2])
