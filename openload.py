# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE

from comm import DWM, match1, echo, start, get_kind_size


class OpenLoad(DWM):     # http://openload.co/
    handle_list = ['openload']

    def __init__(self):
        DWM.__init__(self)
        self.extra_headers['Referer'] = 'https://vjs.zencdn.net/swf/5.1.0/video-js.swf'

    def query_info(self, url):
        # https://openload.co/embed/isCWWnlsZLE/
        # <span id="streamurl">isCWWnlsZLE~1481138074~208.91.0.0~g617lYdo</span>
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        #vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        m = re.search('''<span id="streamurl">([^<>]+)</span>''', hutf)
        vid = m.groups()[0]
        echo(vid)
        url = "https://openload.co/stream/%s?mime=true" % vid

        # https://openload.co/stream/isCWWnlsZLE~1481139117~208.91.0.0~mcLfSy5C?mime=true
        # video/mp4 584989307
        k, tsize = get_kind_size(url)
        k = k.split('/')[-1]
        return self.title, k, [url], tsize


if __name__ == '__main__':
    start(OpenLoad)
