# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, get_kind_size, UTITLE, debug


class OpenLoad(DWM):     # http://openload.co/
    handle_list = ['openload', 'oload\.tv/']

    def __init__(self):
        DWM.__init__(self)
        self.extra_headers['Referer'] = 'https://vjs.zencdn.net/swf/5.1.0/video-js.swf'

    def query_info(self, url):
        # https://openload.co/embed/isCWWnlsZLE/
        # https://openload.io/embed/biw7ytfelzU/
        # <span id="streamurl">isCWWnlsZLE~1481138074~208.91.0.0~g617lYdo</span>
        echo("phantomjs wait 300 ...")
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        debug(hutf)
        #vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        m = re.search('''<span id="streamurl">([^<>]+)</span>''', hutf)
        vid = m.groups()[0]
        echo(vid)
        url = "https://openload.co/stream/%s?mime=true" % vid

        # "https://openload.co/embed/kUEfGclsU9o/"
        n = SelStr("meta[name=og:title]", hutf)
        if n and self.title == UTITLE:
            self.title = n[0]['content']   #="skyrim_no-audio_1080.mp4">"

        # https://openload.co/stream/isCWWnlsZLE~1481139117~208.91.0.0~mcLfSy5C?mime=true
        # video/mp4 584989307
        k, tsize = get_kind_size(url)
        k = k.split('/')[-1]
        if self.title.endswith('.' + k):
            self.title = self.title[:-4]
        return self.title, k, [url], tsize


if __name__ == '__main__':
    start(OpenLoad)
