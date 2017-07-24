# -*- coding: utf8 -*-

from mybs import SelStr
from dailymotion import DM
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
        dm = DM()
        for node in nodes:
            t, e, us, s = dm.query_info(node['href'])
            echo(us)
            urls += us
        return title, None, urls, None

    def get_playlist(self, url):
        ns = SelStr("div.items.sizing li a", self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]


    def test(self, args):
        #url = "http://qdrama.org/k2/"
        hutf = self.get_hutf(args.url)
        #echo(hutf)
        title = SelStr("div.title.sizing h1", hutf)[0].text
        #echo("title =", title)
        nodes = SelStr("div#playsource a", hutf)
        cnt = 1
        for node in nodes:
            echo("%s_%02d" % (title, cnt), node['href'])
            cnt += 1
 

if __name__ == '__main__':
    start(QDRAMA)
