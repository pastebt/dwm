# -*- coding: utf8 -*-

import re
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import UO, DWM, echo, start


class VIDEO66(DWM):
    handle_list = ['/video66\.org/']

    def query_info(self, url):
        # http://video66.org/embed.php?w=798&h=449&vid=vids4/w_2016_-_10_clip3.mp4
        hutf = self.get_hutf(url)
        title = re.search('''"filename":"([^"]+)"''', hutf).group(1)
        if title.endswith('.mp4'):
            title, ext = title[:-4], title[-3:]
            echo(ext)
        echo(title)
        m = re.search("player\.load\(\{\s+file: \"([^\"]+)\",\s+image\:", hutf)
        if m:
            u = m.group(1)
            echo(u)
            u = UO(u, url)
            return title, ext, [u], None
        return None

    #def get_playlist(self, url):
    #    ns = SelStr('div.entry-content.rich-content tr td a',
    #                self.get_hutf(url))
    #    return [(a.text, a['href']) for a in ns]

    def test(self, args):
        '''
        wget -U 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36' -O 10_4.mp4  --header="Referer: http://video66.org/embed.php?w=798&h=449&vid=vids4/w_2016_-_10_clip4.mp4" "http://gateway.play44.net:3010/old/w_2016_-_10_clip4.mp4?st=MTJmZmQ1Yzc0ODM4ZDg5ZWQ4MmMyOTc4NDEyZDRlYzU&e=1497829689"
        '''
        url = "http://video66.org/embed.php?w=798&h=449&vid=vids4/w_2016_-_10_clip4.mp4"
        hutf = self.get_hutf(url)
        m = re.search("player\.load\(\{\s+file: \"([^\"]+)\",\s+image\:", hutf)
        if m:
            u = m.group(1)
            echo(u)
            self.extra_headers['Referer'] = url
            html = self.get_html(u)


if __name__ == '__main__':
    start(VIDEO66)
