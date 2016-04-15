#!/usr/bin/env python
# -*- coding: utf8 -*-


#./phantomjs htl.js 300 http://8drama.com/122804/
#http://8drama.net/ipobar_.php?sign=251438194e51429438981c908a9a1da179242edc4e51&id=gq$$UEN3a0tGazJSeTAyTURROUtEbEdSVkE3TmpGTk95ZEpNaXhFU1RRMlJFRklQQ1UxSnpoUVlHQUtZQW89$$drama&type=html5

import re
import sys
from subprocess import Popen, PIPE

try:
    from HTMLParser import HTMLParser
    p3 = False
except ImportError:
    from html.parser import HTMLParser
    p3 = True

import comm
from comm import DWM, match1, echo


class DRAMA8(DWM):
    def query_info(self, url):
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #echo(html)
        m = re.search("\<source\s* src=\"(http://8drama.net/ipobar_.php[^<> ]+)\"\s* type", hutf)
        if not m:
            return None
        url = m.groups()[0]
        url = HTMLParser().unescape(url)
        #print url
        m = re.search("<title>([^<>]+)</title>", hutf)
        title = m.groups()[0]
        k, size = self.get_total_size([url])
        #print title, k, [url], size
        return title, "mp4", [url], size
        #raise self.ExistsError()


def get_one(page_url, target_dir):
    l = DRAMA8()
    try:
        title, ext, urls, size = l.query_info(page_url)
    except l.ExistsError as e:
        echo(e)
        return
    #l.download_urls(title, ext, urls, size, target_dir)
    p = Popen(["wget", "-O", title + "." + ext, urls[0]])
    p.wait()


def get_list(page_url):
    d = DRAMA8()
    html = d.get_html(page_url)
    hutf = html.decode('utf8')
    m = re.search("""<td width="20%"><a href="(http://8drama.com/\d+/)">""",
                  hutf)
    print m.group()
    yield ""


def usage():
    echo('Usage:', sys.argv[0], '[--playlist] source_url target_dir')
    sys.exit(1)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        usage()

    playlist = False
    while args[0][:2] == '--':
        opt = args.pop(0)
        if opt == '--playlist':
            playlist = True
        else:
            usage()

    if playlist:
        for title, url in get_list(args[0]):
            echo(title, url)
            for i in range(3):
                try:
                    get_one(url, args[1])
                #except KeyboardInterrupt:
                #    raise
                #except socket.ConnectionResetError as e:
                except ConnectionResetError as e:
                    echo(e)
                except Exception: # as e:
                    raise
                else:
                    break
    else:
        get_one(args[0], args[1])
