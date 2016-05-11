#! /usr/bin/python
# -*- coding: utf8 -*-


import sys
from subprocess import Popen


def run(name, cnt):
    cmd = ['cat']
    for i in xrange(1, cnt + 1):
        #cmd.append("tmp/欢乐颂42[%02d].mp4.ts"% i)
        cmd.append("%s[%02d].mp4.ts"% (name, i))
    cmd.append(">")
    cmd.append("%s.ts" % name)
    p = Popen(" ".join(cmd), shell=True)
    p.wait()
    p = Popen(["avconv", "-i", "%s.ts" % name, "-strict", "experimental",
               "-y", "-c", "copy", "%s.mp4" % name])
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
    run(sys.argv[1], i)


if __name__ == '__main__':
    main()
        
    
