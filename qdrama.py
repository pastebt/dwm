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
        import time
        from urllib2 import urlopen
        from urllib import urlencode

        #url = "http://qdrama.org/k2/"
        hutf = self.get_hutf(args.url)
        #echo(hutf)
        title = SelStr("div.title.sizing h1", hutf)[0].text
        #echo("title =", title)
        nodes = SelStr("div#playsource a", hutf)
        cnt = 0
        for node in nodes:
            cnt += 1
            t = "%s_%02d" % (title.encode('utf8'), cnt)
            u = node['href']
            if 'daily' not in u:
                continue
            echo(t, u)
            if cnt < 0:
                continue
            data = urlencode({"aviurl": u,
                              "avitil": t,
                              "destdn": "../dwm/xman/",
                              "sub": "Start"})
            urlopen("http://127.0.0.1:8080/", data).read()
            time.sleep(2)


if __name__ == '__main__':
    start(QDRAMA)
