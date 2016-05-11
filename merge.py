#! /usr/bin/python
# -*- coding: utf8 -*-


import sys
from subprocess import Popen


def run():
    cmd = ['cat']
    for i in xrange(1, 150):
        cmd.append("tmp/欢乐颂42[%02d].mp4.ts"% i)
    cmd.append(">")
    cmd.append("output.ts")
    p = Popen(" ".join(cmd), shell=True)
    p.wait()
    p = Popen(["avconv", "-i", "output.ts", "-strict", "experimental",
               "hls42.mp4"])
    p.wait()


run()
        
    
