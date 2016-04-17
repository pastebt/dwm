#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import sys
import json
import time
import random

try:
    from HTMLParser import HTMLParser
    p3 = False
except ImportError:
    from html.parser import HTMLParser
    p3 = True

from comm import DWM, match1, echo, start



def decode_m3u8(data):
    version = data[0:5]
    if version.lower() == b'vc_01':
        # get real m3u8
        loc2 = data[5:]
        length = len(loc2)
        loc4 = [0] * (2 * length)
        for i in range(length):
            loc4[2 * i] = loc2[i] >> 4
            loc4[2 * i + 1] = loc2[i] & 15
        loc6 = loc4[len(loc4) - 11:] + loc4[:len(loc4) - 11]
        loc7 = [0] * length
        for i in range(length):
            loc7[i] = (loc6[2 * i] << 4) + loc6[2 * i + 1]
        return ''.join([chr(i) for i in loc7])
    else:
        # directly return
        return data


def calcTimeKey(t):
    ror = lambda val, r_bits: ((val & (2 ** 32 - 1)) >> r_bits % 32) | \
                              (val << (32 - (r_bits % 32)) & (2 ** 32 - 1))
    return ror(ror(t, 773625421 % 13) ^ 773625421, 773625421 % 17)


class LETV(DWM):
    def __init__(self):
        DWM.__init__(self)
        ip = "220.181.111.%d" % random.randint(1, 254)
        self.extra_headers = {'X-Forwarded-For': ip, 'Client-IP': ip}

    def query_info(self, url):
        html = self.get_html(url)
        hutf = html.decode('utf8')

        if re.match(r'http://www.letv.com/ptv/vplay/(\d+).html', url):
            vid = match1(url, r'http://www.letv.com/ptv/vplay/(\d+).html')
        else:
            vid = match1(hutf, r'vid="(\d+)"')
        title = match1(hutf, r'name="irTitle" content="(.*?)"')
        echo("vid =", vid)
        echo("title =", title)

        tkey = calcTimeKey(int(time.time()))
        u = 'http://api.letv.com/mms/out/video/playJson?'
        u = u + ("id=%s&platid=1&splatid=101&format=1" % vid)
        u = u + ("&tkey=%d&domain=www.letv.com" % tkey)
        # echo("u =", u)
        data = self.get_html(u)
        # print data
        # info=json.loads(str(data,"utf-8"))
        info = json.loads(data.decode("utf-8"))
        # print info

        stream_id = None
        kwargs = {}
        support_stream_id = info["playurl"]["dispatch"].keys()
        # si = kwargs.get("stream_id", "")
        si = kwargs.get("stream_id", "720p")
        if si and si.lower() in support_stream_id:
            stream_id = si
        else:
            echo("Current Video Supports:")
            for i in support_stream_id:
                echo("\t--format", i, "<URL>")
            if "1080p" in support_stream_id:
                stream_id = '1080p'
            elif "720p" in support_stream_id:
                stream_id = '720p'
            else:
                sids = sorted(support_stream_id, key=lambda i: int(i[1:]))
                stream_id = sids[-1]

        u2 = info["playurl"]["domain"][0]
        u2 = u2 + info["playurl"]["dispatch"][stream_id][0]
        ext = info["playurl"]["dispatch"][stream_id][1].split('.')[-1]
        u2 = u2 + "&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux"
        u2 = u2 + ("&tag=letv&sign=letv&expect=3&tn=%d" % random.random())
        u2 = u2 + ("&pay=0&iscpn=f9051&rateid=%s" % stream_id)

        r2 = self.get_html(u2)
        info2 = json.loads(r2.decode("utf-8"))
        # print info2
        # print info2["location"]
        m3u8 = self.get_html(info2["location"])
        m3u8_list = decode_m3u8(bytearray(m3u8))
        us = re.findall(r'^[^#][^\r]*', m3u8_list, re.MULTILINE)
        # print(ext, us)
        # echo("us[0, 1]", us[0], us[1])
        # echo(len(us))
        #fn = "%s.%s" % (title, ext)
        #if os.path.exists("%s.%s" % (title, ext)):
        #    raise self.ExistsError(fn)
        self.check_exists(title, ext)
        k, size = self.get_total_size(us)
        return title, ext, us, size

    def get_list(self, page_url):
        html = self.get_html(page_url)
        #echo(html)
        hutf = html.decode('utf8')
        #echo(hutf)
        m = MyHTMLParser()
        m.feed(hutf[1000:])
        #echo(m.urllist)
        #return []
        return m.urllist


#def get_one(page_url, target_dir):
#    l = LETV()
#    try:
#        title, ext, urls, size = l.query_info(page_url)
#    except l.ExistsError as e:
#        echo(e)
#        return
#    l.download_urls(title, ext, urls, size, target_dir)


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        #self.p = 0
        self.urllist = []

    def handle_starttag(self, tag, attrs):
        # python3 letv.py --playlist http://www.letv.com/tv/10003313.html .
        # 女医明妃传
        if tag != 'a':
            return
        if len(attrs) != 3:
            return
        ats = dict(attrs)
        if ats.get('target') != '_blank':
            return
        u = ats.get('href')
        if not re.match(r'http://www.letv.com/ptv/vplay/(\d+).html', u):
            return

        T = ats.get('title')
        if p3:
            t = T
        else:
            t = T.encode('utf8')
        if not re.match('^女医明妃传\d\d$', t):
            return

        self.urllist.append([t, u])

    #def handle_starttag(self, tag, attrs):
    #    if tag == 'p' and len(attrs) == 1 and dict(attrs).get('class') == 'p1':
    #        self.p = 1
    #    if self.p and tag == 'a':
    #        for k, v in attrs:
    #            echo(k, v)

    #def handle_endtag(self, tag):
    #    if tag == 'p':
    #        self.p = 0


#def usage():
#    echo('Usage:', sys.argv[0], '[--playlist] source_url target_dir')
#    sys.exit(1)


if __name__ == '__main__':
    start(LETV)
#    args = sys.argv[1:]
#    if len(args) < 2:
#        usage()
#
#    playlist = False
#    while args[0][:2] == '--':
#        opt = args.pop(0)
#        if opt == '--playlist':
#            playlist = True
#        else:
#            usage()
#
#    if playlist:
#        for title, url in get_list(args[0]):
#            echo(title, url)
#            for i in range(3):
#                try:
#                    get_one(url, args[1])
#                #except KeyboardInterrupt:
#                #    raise
#                #except socket.ConnectionResetError as e:
#                except ConnectionResetError as e:
#                    echo(e)
#                except Exception: # as e:
#                    raise
#                else:
#                    break
#    else:
#        get_one(args[0], args[1])