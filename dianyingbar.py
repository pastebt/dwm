#!/usr/bin/env python
# -*- coding: utf8 -*-

import re
import sys
#from subprocess import Popen, PIPE
#from html.parser import HTMLParser

from comm import DWM, match1, echo, start


class DYB(DWM):     #dianyingbar
    def __init__(self):
        DWM.__init__(self)
        self.extra_headers = {'Referer': "http://bodekuai.duapp.com/ckplayer/ckplayer.swf"}

    def query_info(self, url):
        # get xml
        html = self.get_html(url)
        hutf = html.decode('utf8')
        ret = re.findall("videoarr.push\('YKYun\.php\?id\=([^\(\)]+)'\)", hutf)
        print(ret[0])
        url = "http://bodekuai.duapp.com/api/yUrl.php?id=" + ret[0]
        # get flv part list
        html = self.get_html(url)
        hutf = html.decode('utf8')
        ret = re.findall("<video><file><\!\[CDATA\[([^<>]+)\]\]></file>"
                         "<size>(\d+)</size>"
                         "<seconds>\d+</seconds></video>",
                         hutf)
        print(ret)
        urls = []
        total_size = 0
        for u, s in ret:
            urls.append(u)
            total_size += int(s)
        return "test", "flv", urls, total_size

    #def query_info1(self, url):
    #    # title, ext, urls, totalsize
    #    sys.path.insert(1, '../you-get/src')
    #    from you_get.extractors.iqiyi import Iqiyi
    #    i = Iqiyi(url)
    #    i.prepare()

    #    i.streams_sorted = [dict([('id', stream_type['id'])] + list(i.streams[stream_type['id']].items())) for stream_type in Iqiyi.stream_types if stream_type['id'] in i.streams]
    #    i.extract()
    #    #echo(i.streams_sorted)
    #    stream_id = i.streams_sorted[0]['id']
    #    echo(stream_id)
    #    echo(i.title)
    #    #echo(i.streams)
    #    urls = i.streams[stream_id]['src']
    #    ext = i.streams[stream_id]['container']
    #    total_size = i.streams[stream_id]['size']
    #    title = self.align_title_num(i.title)
    #    self.check_exists(title, ext)
    #    return title, ext, urls, total_size

    def get_list(self, page_url):
        p = Popen(["./phantomjs", "dwm.js", "600", page_url], stdout=PIPE)
        html = p.stdout.read()
        p.wait()
        #html = self.get_html(page_url)
        #echo(html)
        hutf = html.decode("utf8")
        #echo(hutf)
        c = hutf.split("<!--视频列表区域 -->")[1]
        m = MyHTMLParser("")
        m.feed(c)
        #echo(m.urllist)
        self.align_num = len(str(len(m.urllist)))
        return m.urllist


if __name__ == '__main__':
    start(DYB)
