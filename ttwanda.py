# -*- coding: utf8 -*-

import os
import re
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, debug, py3


class TTWanDa(DWM):     # http://www.ttwanda.com/
    #handle_list = ['ttwanda\.com/films/']

    def query_info(self, url):
        #url = 'http://www.ttwanda.com/films/us/2091.html?ac'
        echo("phantomjs wait 10 ...")
        p = Popen(["./phantomjs", "dwm.js", "10", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        debug(hutf)
        title = SelStr("div.video-content article p strong", hutf)[0].text
        r = "《(.+)》"
        if not py3:
            r = r.decode('utf8')
        t = match1(title, r)
        if t:
            title = t
        echo(title)
        urls = []
        src = SelStr('body > div#a1 > video', hutf)
        if src: # m3u8
            src = src[0]['src']
            for line in self.get_html(src).split('\n'):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                urls.append(line)
        else:
            # http://www.ttwanda.com/films/us/1693.html?xf
            pu = match1(hutf, 'var play_url \= "([^"])"')
            urls.append(pu)
        debug(urls)
        #k, s = self.get_total_size(urls)
        return title, 'flv', urls, None


if __name__ == '__main__':
    start(TTWdanDa)
    #TTWanDa().query_info(1)
