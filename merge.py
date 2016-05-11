#! /usr/bin/python
# -*- coding: utf8 -*-


import sys
from subprocess import Popen


def run1(name, cnt):
    cmd = ["avconv"]
    for i in xrange(1, cnt + 1):
        cmd.append("-i")
        cmd.append("%s[%02d].mp4"% (name, i))
    cmd.append("-y")
    cmd.append("-c")
    cmd.append("copy")
    cmd.append("%s.mp4" % name)
    p = Popen(cmd)
    p.wait()


def merge(name, ext, cnt):
    cmd = ['cat']
    for i in xrange(cnt):
        #cmd.append("tmp/欢乐颂42[%02d].mp4.ts"% i)
        cmd.append("%s[%02d].%s.ts"% (name, ext, i))
    cmd.append(">")
    tmpfn = "%s.%s.ts" % (name, ext)
    cmd.append(tmpfn)
    p = Popen(" ".join(cmd), shell=True)
    p.wait()
    p = Popen(["avconv", "-i", tmpfn, "-strict", "experimental",
               "-y", "-c", "copy", "%s.%s" % (name, ext)])
    p.wait()


def usage():
    print 'Usage:', sys.argv[0], "name max_id"
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        usage()
    try:
        i = int(sys.argv[2])
    except:
        usage()
    merge(sys.argv[1], "mp4", i)


if __name__ == '__main__':
    main()
        
    
