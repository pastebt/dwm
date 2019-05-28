# -*- coding: utf8 -*-

import re
import json

from comm import DWM, echo, start


class DM(DWM):     # http://www.dailymotion.com/embed/video/
    handle_list = ['/www.dailymotion.com/embed/video/',
                   '/www.dailymotion.com/video/']

    def query_info(self, url):
        #url = "http://www.dailymotion.com/embed/video/k7alsxAgBgcMGaachYS"
        #url = "http://www.dailymotion.com/embed/video/k4BjypcByJGUTDl6Bvx"
        hutf = self.get_hutf(url)
        #echo(hutf)
        # "720":[{"type":"application\/x-mpegURL","url":"http:\/\/www.dailymotion.com\/cdn\/manifest\/video\/x2hpv0i.m3u8?auth=1482432896-2562-0fq84z9d-24047244e9a36f0f3fab8388642b74c1&include=720"},{"type":"video\/mp4","url":"http:\/\/www.dailymotion.com\/cdn\/H264-1280x720\/video\/x2hpv0i.mp4?auth=1482432896-2562-pvg451ll-4c251ca9aa8a1bf6f56c88d318eccd65"}]}
        m = re.search("var config = ([^\n]+);", hutf)
        j = json.loads(m.group(1))
        mr, mq, mu, ex = -2, '', '', ''
        qua = ['auto', '144', '240', '380', '480', '720']
        for k, vs in j['metadata']['qualities'].items():
            if k not in qua:
                echo("New qua", k)
                continue
            r = qua.index(k)
            if r > mr:
                for v in vs:
                    t = v.get('type', '')
                    if t.startswith('video/'):
                        mr, mq = r, k
                        mu = v['url']
                        ex = t[-3:]
        echo("ext=%s, mq=%s, url=%s" % (ex, mq, mu))
        title = j['metadata']['title'].strip('.')
        return title, ex, [mu], None

    def test(self):
        url = 'http://www.dailymotion.com/video/k336RLStrzbIGzl96CY'
        url = 'http://www.dailymotion.com/embed/video/k6ELdHzeVXWQmemlHkY&info=0'


if __name__ == '__main__':
    start(DM)
