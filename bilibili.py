# -*- coding: utf8 -*-

import re
import sys
import hashlib
from copy import copy

from mybs import SelStr
from comm import DWM, echo, start, debug, search_first, match1, UTITLE, run


appkey = 'f3bb208b3d081dc8'
SECRETKEY_MINILOADER = '1c15888dc316e05a15fdd0a02ed6584f'


class BILIBILI(DWM):
    sp = False
    handle_list = ["\.bilibili\.com/video/av\d+/",
                   "\.bilibili\.com/sp/"]

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
        vtitle = SelStr('div.v-title > h1', hutf)[0].text
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
        #echo("m title =[%s]" % title)
        m = re.search(u"(\d+)、.+", title)
        #if m and m.group(1) == m.group(2):
        #if m and BILIBILI.sp:
        if m:
            n = int(m.group(1)) - 1
            if BILIBILI.sp:
                if self.title == UTITLE:
                    title = "%s[%02d]" % (cid, n)
                else:
                    title = "%s[%02d]" % (self.title, n)
            else:
                title = ("E%02d_" %  (n + 1)) + vtitle
        #else:
        #    echo("m =", m)
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

    def handle_sp_list(self, url):
        # serial play list
        urls = []
        # http://www.bilibili.com/sp/维京传奇
        # base.special.js line 25, loadBgmPage
        # http://www.bilibili.com/sppage/bangumi-21542-913-1.html
        # first find 21542
        hutf = self.get_hutf(url)
        #echo(hutf)
        spid = search_first(hutf, 'var spid = "(\d+)";').group(1)
        echo("spid=", spid)
        for li in SelStr('ul#season_selector li', hutf):
            data = self.get_hutf("http://www.bilibili.com/sppage/bangumi-%s-%s-1.html" % (
                                 spid, li['season_id']))
            for n in SelStr('div.season_list li a.t', data):
                urls.append((n['title'].strip(),
                            'http://www.bilibili.com' + n['href']))
        args = copy(self.parsed_args)
        sk = args.playlist_skip
        args.playlist_skip = -1315
        tp = args.playlist_top
        args.playlist_top = 0
        cnt = 0
        for t, u in urls:
            cnt = cnt + 1
            if cnt > tp > 0:
                break
            if cnt < sk:
                continue
            echo(t, u)
            b = BILIBILI()
            b.title = t
            args.url = u
            run(b, args)
        sys.exit(1)

    def get_playlist(self, url):
        if "bilibili.com/sp/" in url:
            BILIBILI.sp = True
            self.handle_sp_list(url)
        h, p = self.get_h_p(url)
        hutf = self.get_hutf(url)
        m = re.search("<option value='(/%s/index_\d+.html)' selected>"
                      "([^<>]+)</option>" % p, hutf)
        if m:
            pl = [(m.group(1), m.group(2))]
        else:
            pl = re.findall("<option value='(/%s/index_\d+.html)'>"
                            "([^<>]+)</option>" % p, hutf)
        return [(self.align_title_num(t), h + u) for u, t in pl]


if __name__ == '__main__':
    start(BILIBILI)
