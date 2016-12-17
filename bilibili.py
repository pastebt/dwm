#! /usr/bin/python
# -*- coding: utf8 -*-

import re
import sys
import hashlib

from comm import DWM, echo, start, debug, search_first


appkey = 'f3bb208b3d081dc8'
SECRETKEY_MINILOADER = '1c15888dc316e05a15fdd0a02ed6584f'


class BILIBILI(DWM):
    def query_info(self, url):
        # http://www.bilibili.com/video/av2812495/
        h, p = self.get_h_p(url)
        html = self.get_html(url)
        hutf = html.decode('utf8')
        m = search_first(hutf,
                         "<option value='/%s/index_\d+.html' selected>"
                         "([^<>]+)</option>" % p,
                         "<option value='/%s/index_\d+.html'>"
                         "([^<>]+)</option>" % p,
                         '<div class="v-title"><h1 title="([^<>]+)"')
        title = m.group(1)
        title = self.align_title_num(title)
        #echo(title.encode('utf8'))
        echo(title)
        #return
        m = re.search('''cid=(\d+)&''', hutf)
        cid = m.group(1)
        echo("cid =", cid)

        #html = self.get_html('http://interface.bilibili.com/playurl?appkey=' +
        #                     self.appkey + '&cid=' + cid)
        surl = self.sign_url(cid)
        html = self.get_html(surl)
        #echo(html)
        #return
        hutf = html.decode('utf8')
        ms = re.findall('<durl>\s+<order>\d+</order>\s+'
                       '<length>\d+</length>\s+<size>(\d+)</size>\s+'
                       '<url><\!\[CDATA\[([^<>]+)]]></url>', hutf, re.M)
        if ms:
            ext = ms[0][1].split('?')[0][-3:]
            totalsize = 0
            urls = []
            for s, u in ms:
                totalsize += int(s)
                urls.append(u)
        else:
            ms = re.findall('<durl>\s+<order>\d+</order>\s+'
                            '<length>\d+</length>\s+'
                            '<url><\!\[CDATA\[([^<>]+)]]></url>', hutf, re.M)
            urls = ms[:]
            k, totalsize = self.get_total_size(urls)
            #print "k=[%s]" % k
            #ext = k.split('-')[1]
            ext = "flv"
        return title, ext, urls, totalsize

    def sign_url(self, cid):
        #sign_this = hashlib.md5(bytes('cid={cid}&from=miniplay&player=1{SECRETKEY_MINILOADER}'.format(cid = cid, SECRETKEY_MINILOADER = SECRETKEY_MINILOADER), 'utf-8')).hexdigest()
        s = 'cid=%s&from=miniplay&player=1%s' % (cid, SECRETKEY_MINILOADER)
        sign_this = hashlib.md5(s.encode('utf8')).hexdigest()
        return 'http://interface.bilibili.com/playurl?&cid=' + cid + '&from=miniplay&player=1' + '&sign=' + sign_this

    def get_h_p(self, url):
        # http://www.bilibili.com/video/av4197196/
        m = re.match("(https?://[^/]+)/(video/av\d+)", url)
        if not m:
            raise Exception("Unsupport bilibili url format")
        return m.group(1), m.group(2)

    def get_playlist(self, url):
        h, p = self.get_h_p(url)
        #print h, p
        html = self.get_html(url)
        hutf = html.decode('utf8')
        m = re.search("<option value='(/%s/index_\d+.html)' selected>"
                      "([^<>]+)</option>" % p, hutf)
        if m:
            pl = [(m.group(1), m.group(2))]
        else:
            pl = re.findall("<option value='(/%s/index_\d+.html)'>"
                            "([^<>]+)</option>" % p, hutf)
        #print pl
        return [(self.align_title_num(t), h + u) for u, t in pl]

    @classmethod
    def can_do_it(cls, url):
        return ".bilibili.com/" in url


if __name__ == '__main__':
    start(BILIBILI)
