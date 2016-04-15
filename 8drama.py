#!/usr/bin/env python
# -*- coding: utf8 -*-


#./phantomjs htl.js 300 http://8drama.com/122804/
#http://8drama.net/ipobar_.php?sign=251438194e51429438981c908a9a1da179242edc4e51&id=gq$$UEN3a0tGazJSeTAyTURROUtEbEdSVkE3TmpGTk95ZEpNaXhFU1RRMlJFRklQQ1UxSnpoUVlHQUtZQW89$$drama&type=html5

import re
import sys
from subprocess import Popen, PIPE

try:
    from HTMLParser import HTMLParser
    import httplib
    import urlparse
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
        p.wait()
        #print html
        m = re.search("\<source\s* src=\"(http://8drama.net/ipobar_.php[^<> ]+)\"\s* type", html)
        if not m:
            return None
        url = m.groups()[0]
        url = HTMLParser().unescape(url)
        print url
        k, size = self.get_total_size([url])
        return "TITLE", k, [url], size
        #raise self.ExistsError()


def get_kind_size0(url):
    # step 1
    hd = {'Referer': 'http://vjs.zencdn.net/4.12/video-js.swf', 'DNT': 1}
    url_parts = urlparse.urlsplit(url)
    conn = httplib.HTTPConnection(url_parts[1])
    q = urlparse.urlunsplit(("", "", url_parts[2], url_parts[3], ""))
    conn.request("HEAD", q) #, "", hd)
    resp = conn.getresponse()
    echo("data1 =", resp.read())
    conn.close()
    echo(resp.status, resp.reason)
    echo(resp.getheaders())

    print 'step 2'
    url = resp.getheader('Location', '')
    print url
    url_parts = urlparse.urlsplit(url)
    print url_parts[0]
    conn = httplib.HTTPSConnection(url_parts[1])
    q = urlparse.urlunsplit(("", "", url_parts[2], url_parts[3], ""))
    #hd = {'Referer': 'http://vjs.zencdn.net/4.12/video-js.swf', 'DNT': 1,
    #      'Connection': 'keep-alive',   }
          #'Host': url_parts[1], }
    conn.request("HEAD", q) #, "", hd)
    resp = conn.getresponse()
    echo("data1 =", resp.read())
    conn.close()
    echo(resp.status, resp.reason)
    echo(resp.getheaders())
 
    return '', 1


def get_kind_size(u):
    url = u
    while url:
        url_parts = urlparse.urlsplit(url)
        if url_parts[0] == 'https':
            conn = httplib.HTTPSConnection(url_parts[1])
        else:
            conn = httplib.HTTPConnection(url_parts[1])
        # print url_parts
        q = urlparse.urlunsplit(("", "", url_parts[2], url_parts[3], ""))
        #print h
        conn.request("HEAD", q) #, "", h)
        resp = conn.getresponse()
        #echo("data1 =", resp.read())
        conn.close()
        #echo(resp.getheaders())
        #echo(resp.status, resp.reason)
        #if resp.status == 302:
        url = resp.getheader('Location', '')
    size = int(resp.getheader('Content-Length', '0'))
    kind = resp.getheader('Content-Type', '')
    return kind, size


comm.get_kind_size = get_kind_size


def get_one(page_url, target_dir):
    l = DRAMA8()
    try:
        title, ext, urls, size = l.query_info(page_url)
    except l.ExistsError as e:
        echo(e)
        return
    #l.download_urls(title, ext, urls, size, target_dir)


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
