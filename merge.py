#! /usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import shutil
from subprocess import Popen, PIPE, CalledProcessError

from comm import echo


def run1(name, cnt):
    cmd = ["avconv"]
    for i in range(1, cnt + 1):
        cmd.append("-i")
        cmd.append("%s[%02d].mp4"% (name, i))
    cmd.append("-y")
    cmd.append("-c")
    cmd.append("copy")
    cmd.append("%s.mp4" % name)
    p = Popen(cmd)
    p.wait()


def merge1(name, ext, cnt):
    cmd = ['cat']
    for i in range(cnt):
        #cmd.append("tmp/欢乐颂42[%02d].mp4.ts"% i)
        cmd.append("%s[%02d].%s.ts"% (name, i, ext))
    cmd.append(">")
    tmpfn = "%s.%s.ts" % (name, ext)
    cmd.append(tmpfn)
    p = Popen(" ".join(cmd), shell=True)
    p.wait()
    p = Popen(["avconv", "-i", tmpfn, "-strict", "experimental",
               "-y", "-c", "copy", "%s.%s" % (name, ext)])
    p.wait()


def merge(name, ext, cnt, clean=False):
    # avconv -i tmp/嘻哈帝国第一季12[99].mp4 -c copy -f mpegts - > aa.ts
    cmd = ["avconv", "-i", "-", "-y", "-c", "copy", "%s.%s" % (name, ext)]
    p = Popen(cmd, stdin=PIPE)
    fs = []
    for i in range(cnt):
        fs.append("%s[%02d].%s.ts"% (name, i, ext))
    for f in fs:
        fobj = open(f, "r+b")
        shutil.copyfileobj(fobj, p.stdin)
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, cmd)
    if clean:
        for f in fs:
            os.remove(f)


def usage():
    echo('Usage:', sys.argv[0], "name url_num")
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
        
    
