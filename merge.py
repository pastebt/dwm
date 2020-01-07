#! /usr/bin/python -B
# -*- coding: utf8 -*-

import os
import sys
import shutil
from time import sleep
from subprocess import Popen, PIPE, CalledProcessError

from comm import echo


def run1(name, cnt):
    cmd = ["avconv"]
    for i in range(1, cnt + 1):
        cmd.append("-i")
        cmd.append("%s[%02d].mp4" % (name, i))
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
        cmd.append("%s[%02d].%s.ts" % (name, i, ext))
    cmd.append(">")
    tmpfn = "%s.%s.ts" % (name, ext)
    cmd.append(tmpfn)
    p = Popen(" ".join(cmd), shell=True)
    p.wait()
    p = Popen(["avconv", "-i", tmpfn, "-strict", "experimental",
               "-y", "-c", "copy", "%s.%s" % (name, ext)])
    p.wait()


tss = ('ts', 'x-mpeg-ts', 'mp2t', 'MP2T')


def find_tool():
    p = Popen(['which', 'ffmpeg'])
    p.wait()
    if p.returncode == 0:
        return "ffmpeg"

    p = Popen(['which', 'avconv'])
    p.wait()
    if p.returncode == 0:
        return "avconv"
    return ""


def merge(name, ext, cnt, clean=False, ists=False):
    # ext = 'x-mpeg-ts'
    # avconv -i 12.mp4 -c copy -f mpegts -bsf h264_mp4toannexb - > aa.ts
    oex = ext
    if ext in tss:
        ists = True
        oex = "mp4"
    outfn = "%s.%s" % (name, oex)
    mrgfn = "%s.mrg.%s" % (name, oex)
    if os.path.exists(outfn):
        echo(outfn, "exists")
        return
    fs = []
    for i in range(cnt):
        fs.append("%s[%02d].%s" % (name, i, ext))
        #fs.append("%s%03d.%s" % (name, i + 1, ext))

    cmd = ["avconv",
           "-v", "error",
           "-i", "-",
           "-y",
           "-c", "copy",
           #"-bsf", "h264_mp4toannexb",
           mrgfn]
    p = Popen(cmd, stdin=PIPE)
    for f in fs:
        echo("merge", f, "/", cnt)
        try:
            s = None
            if ists:
                fobj = open(f, "r+b")
            else:
                fobj = open(f + ".ts", "r+b")
        except IOError:
            smd = ["avconv",
                   #'-loglevel', #'quiet', "error",
                   "-v", "error",
                   "-i", f,
                   "-c", "copy",
                   "-f", "mpegts",
                   "-bsf", "h264_mp4toannexb",
                   "-"]
            s = Popen(smd, stdout=PIPE)
            fobj = s.stdout
        shutil.copyfileobj(fobj, p.stdin)
        if s:
            s.wait()
            s.stdout.close()
            if s.returncode != 0:
                #echo("s.returncode =", s.returncode)
                raise CalledProcessError(s.returncode, smd)
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, cmd)
    os.rename(mrgfn, outfn)

    if clean:
        for f in fs:
            os.remove(f)
            os.remove(f + ".ts")


def waitp(p, timeout=0):
    if timeout <= 0:
        p.wait()
        return p.returncode

    while timeout > 0:
        timeout -= 1
        sleep(1)
        p.poll()
        if not p.returncode is None:
            break
    if p.returncode is None:
        p.kill()
        p.terminate()

    return p.returncode


def m3u8_merge(url, outfn, slow=False):
    #outfn = name + ".mp4"
    #url = "%s.dwm/%s.m3u8" % (name, name)
    tool = find_tool()
    if not tool:
        return
    if slow:
        cmds = [tool,
            "-allowed_extensions", "ALL",
            "-i", url,
            "-f", "mp4",
            outfn + ".dwm",
            ]
    else:
        cmds = [tool,
            "-allowed_extensions", "ALL",
            "-i", url,
            #"-acodec", "copy",
            #"-vcodec", "copy",
            "-c", "copy",
            "-f", "mp4",
            outfn + ".dwm",
            ]
    #debug(cmds)
    p = Popen(cmds, env={"LANG": "en_CA.UTF-8"})
    p.wait()
    if p.returncode == 0:
        os.rename(outfn + ".dwm", outfn)
        echo(outfn)


def usage():
    echo('Usage:', sys.argv[0], "name ext url_num [ists]")
    echo('Usage:', sys.argv[0], "m3u8 name")
    echo('Usage:', sys.argv[0], "slow name")
    sys.exit(1)


def main():
    if len(sys.argv) == 3 and sys.argv[1] in ('m3u8', 'slow'):
        name = sys.argv[2]
        if name.endswith(".dwm"):
            name = name[:-4]
        outfn = name + ".mp4"
        url = "%s.dwm/%s.m3u8" % (name, name)
        m3u8_merge(url, outfn, sys.argv[1] == 'slow')
        return
    if len(sys.argv) not in (4, 5):
        usage()
    try:
        i = int(sys.argv[3])
    except:
        usage()
    if len(sys.argv) == 4:
        merge(sys.argv[1], sys.argv[2], i)
    elif len(sys.argv) == 5 and sys.argv[4] == 'ists':
        merge(sys.argv[1], sys.argv[2], i, False, True)
    else:
        usag()


if __name__ == '__main__':
    main()
