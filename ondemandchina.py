# -*- coding: utf8 -*-

from subprocess import Popen, PIPE

from mybs import SelStr
from chrome import get_ci
from comm import DWM, echo, start, debug


class ODC(DWM):
    handle_list = ['/ondemandchina\.com/']

    def query_info(self, url):
        # http://8drama.com/122804/
        #http://8drama.net/ipobar_.php?sign=251438...
        echo('phantomjs wait ...')
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        url = SelStr('video source', hutf)[0]['src']
        title = SelStr('h1.entry-title', hutf)[0].text
        return title, None, [url], None

    def get_playlist(self, url):
        ns = SelStr('div.entry-content.rich-content tr td a',
                    self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]

    def test(self, args):
        url = "https://www.ondemandchina.com/zh-Hans/watch/jade-dynasty/movie-1"
        hutf = self.get_hutf(url)
        echo(hutf)



if __name__ == '__main__':
    start(ODC)
