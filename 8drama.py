# -*- coding: utf8 -*-

from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start


class DRAMA8(DWM):
    handle_list = ['/8drama\.com/']

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


if __name__ == '__main__':
    start(DRAMA8)
