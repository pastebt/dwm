# -*- coding: utf8 -*-

from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start


class IFVOD(DWM):
    handle_list = ['/ifvod\.tv/']

    def query_info(self, url):
        return title, None, [url], None

    def get_playlist(self, url):
        ns = SelStr('div.entry-content.rich-content tr td a',
                    self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]

    def test(self, args):
        url = 'https://www.ifvod.tv/detail?id=zEplg9yO88S'


if __name__ == '__main__':
    start(IFVOD)
