#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from subprocess import Popen, PIPE

#try:
#    from HTMLParser import HTMLParser
#except ImportError:
#    from html.parser import HTMLParser

from mybs import SelStr
from comm import DWM, match1, echo, start


class IQIYI(DWM):
    handle_list = [".iqiyi.com/"]

    def query_info(self, url):
        # title, ext, urls, totalsize
        sys.path.insert(1, '../you-get/src')
        from you_get.extractors.iqiyi import Iqiyi
        i = Iqiyi(url)
        i.prepare()

        i.streams_sorted = [dict([('id', stream_type['id'])] + list(i.streams[stream_type['id']].items())) for stream_type in Iqiyi.stream_types if stream_type['id'] in i.streams]
        i.extract()
        #echo(i.streams_sorted)
        stream_id = i.streams_sorted[0]['id']
        echo(stream_id)
        echo(i.title)
        #echo(i.streams)
        urls = i.streams[stream_id]['src']
        ext = i.streams[stream_id]['container']
        total_size = i.streams[stream_id]['size']
        title = self.align_title_num(i.title)
        self.check_exists(title, ext)
        return title, ext, urls, total_size

    def get_playlist(self, page_url):
        # http://www.iqiyi.com/a_19rrhb9eet.html 太阳的后裔
        echo("get_list phantomjs wait 600 ...")
        p = Popen(["./phantomjs", "dwm.js", "600", page_url], stdout=PIPE)
        html = p.stdout.read()
        p.wait()
        hutf = html.decode("utf8")
        #c = hutf.split("<!--视频列表区域 -->")[1]
        urls = [(a.text, a['href']) for a in SelStr('div.smalList > ul > li > a', hutf)]
        self.align_num = len(str(len(urls)))
        #echo(urls)
        return urls


if __name__ == '__main__':
    start(IQIYI)
