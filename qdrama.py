# -*- coding: utf8 -*-

from mybs import SelStr
from comm import DWM, echo, start


class QDRAMA(DWM):
    handle_list = ['/qdrama\.org/']

    def query_info(self, url):
        hutf = self.get_hutf(url)
        #echo(hutf)
        title = SelStr("div.title.sizing h1", hutf)[0].text
        #echo("title =", title)
        nodes = SelStr("div#playsource a", hutf)
        urls = []
        for node in nodes:
            urls.append(node['href'])
        return title, None, urls, None

    def get_playlist(self, url):
        ns = SelStr("div.items.sizing li a", self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]


    def test(self, args):
        url = "http://qdrama.org/k2/"
        hutf = self.get_hutf(url)
        echo(hutf)


if __name__ == '__main__':
    start(QDRAMA)
