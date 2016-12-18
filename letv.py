#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import sys
import json
import time
import random

from mybs import SelStr
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
    handle_list = ['.letv.com/', '.le.com/']

    def __init__(self):
        DWM.__init__(self)
        ip = "220.181.111.%d" % random.randint(1, 254)
        self.extra_headers = {'X-Forwarded-For': ip, 'Client-IP': ip}

    def query_info(self, url):
        #'http://www.le.com/ptv/vplay/1877906.html?ch=sougou_mfdy&fromvsogou=1'
        html = self.get_html(url)
        hutf = html.decode('utf8')

        if re.match(r'http://www.le.com/ptv/vplay/(\d+).html', url):
            vid = match1(url, r'http://www.le.com/ptv/vplay/(\d+).html')
        elif re.match(r'http://www.letv.com/ptv/vplay/(\d+).html', url):
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
        #u = u + ("&tkey=%d&domain=www.le.com" % tkey)
        data = self.get_html(u)
        info = json.loads(data.decode("utf-8"))

        stream_id = None
        kwargs = {}
        support_stream_id = info["playurl"]["dispatch"].keys()
        si = kwargs.get("stream_id", "")
        if self.is_playlist:
            si = kwargs.get("stream_id", "720p")
        else:
            si = kwargs.get("stream_id", "1080p")
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
        echo("stream_id =", stream_id)
        u2 = info["playurl"]["domain"][0]
        u2 = u2 + info["playurl"]["dispatch"][stream_id][0]
        ext = info["playurl"]["dispatch"][stream_id][1].split('.')[-1]
        u2 = u2 + "&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux"
        u2 = u2 + ("&tag=letv&sign=letv&expect=3&tn=%d" % random.random())
        u2 = u2 + ("&pay=0&iscpn=f9051&rateid=%s" % stream_id)

        r2 = self.get_html(u2)
        info2 = json.loads(r2.decode("utf-8"))
        m3u8 = self.get_html(info2["location"])
        m3u8_list = decode_m3u8(bytearray(m3u8))
        us = re.findall(r'^[^#][^\r]*', m3u8_list, re.MULTILINE)
        return title, ext, us, None

    def get_playlist(self, page_url):
        # http://www.letv.com/tv/10003313.html
        # http://www.le.com/tv/10009472.html
        urls = []
        hutf = self.get_hutf(page_url)
        for a in SelStr('div.list.active > dl > dt > a', hutf):
            i = a.select("img")[0]
            if 'title' in i:
                urls.append((i['title'], a['href']))
        return urls


if __name__ == '__main__':
    start(LETV)
