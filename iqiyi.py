# -*- coding: utf8 -*-

import sys
import time
import json
import random
import hashlib
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, debug


class I2(DWM):
    # http://cn-proxy.com/
    def __init__(self):
        #DWM.__init__(self)
        #DWM.__init__(self, proxy='auto')
        #DWM.__init__(self, proxy={'http': 'https://secure.uku.im:993'})
        DWM.__init__(self, proxy={'http': 'http://117.177.243.6:8080'})
        #ip = "220.181.111.%d" % random.randint(1, 254)
        ip = "117.177.243.6"
        self.extra_headers['X-Forwarded-For'] = ip
        self.extra_headers['Client-IP'] = ip

    def getVMS(self, tvid, vid):
        t = int(time.time() * 1000)
        src = '76f90cbd92f94a2e925d83e8ccd22cb7'
        key = 'd5fb4bd9d50c4be6948c97edd7254b0e'
        msg = (str(t) + key + vid).encode('utf-8')
        #sc = hashlib.new('md5',
        #                 bytes(str(t) + key + vid,
        #                       'utf-8')).hexdigest()
        sc = hashlib.new('md5', msg).hexdigest()
        #u = 'http://cache.m.iqiyi.com/tmts' + \
        #    '/{0}/{1}/?t={2}&sc={3}&src={4}'.format(tvid,
        #                                            vid,
        #                                            t, sc, src)
        u = "http://cache.m.iqiyi.com/tmts/%s/%s/?t=%d&sc=%s&src=%s" % (
             tvid, vid, t, sc, src)
        #data = self.get_hutf(vmsreq)
        data = self.get_hutf(u)
        echo(data)
        return json.loads(data)


class IQIYI(DWM):
    handle_list = [".iqiyi.com/"]

    def get_vd_url(self, dat):
        for vd in (4,   # TD: '720p'
                   17,  # TD_H265': 720p H265
                   2,   # HD: '540p'
                   5,   # BD: 1080p
                    ):
            for stream in dat['data']['vidl']:
                if vd == stream["vd"]:
                    echo("4, 17, 2, 5, vd =", vd)
                    url = stream['m3u']
                    return vd, url
        else:
            vd = dat['data']['vidl'][0]['vd']
            #echo("vd =", dat['data']['vidl'][0]['vd'])
            url = dat['data']['vidl'][0]['m3u']
            return vd, url

    def query_info(self, url):
        # title, ext, urls, totalsize
        #url = "http://www.iqiyi.com/v_19rr26qr38.html"
        #url = "https://www.iqiyi.com/v_19rr04z9is.html?list=19rrm106om"
        #url = "https://www.iqiyi.com/v_19rr04z9is.html"
        hutf = self.get_hutf(url)
        for s in ('meta[name=irTitle]',
                  'meta[property=og:title]'):
            try:
                title = SelStr(s, hutf)[0]["content"]
                break
            except IndexError:
                title = self.title
        #echo(hutf)
        tvid = match1(hutf, """param\['tvid'\] = "(\d+)";""")
        vid = match1(hutf, """param\['vid'\] = "([^"]+)";""")
        echo("tvid=", tvid, ", vid=", vid)
        dat = I2().getVMS(tvid, vid)
        #echo(dat)
        vd, url = self.get_vd_url(dat)
        #title = "%s_vd%02d" % (title, vd)
        echo(title)
        #return
        hutf = self.get_hutf(url)
        us = self._get_m3u8_urls(url, hutf)
        if '.ts?' in us[0]:
            return title, "ts", us, None
        # title, ext, urls, totalsize
        return title, None, us, None

    def get_playlist(self, page_url):
        #http://www.iqiyi.com/playlist521743802.html
        if '/playlist' in url:
            hutf = self.get_hutf(url)
            els = SelStr("div.site-piclist_pic > a.site-piclist_pic_link",
                         hutf)
            return [(e['title'], e['href']) for e in els]

        # http://www.iqiyi.com/a_19rrhb9eet.html 太阳的后裔
        echo("get_list phantomjs wait 200 ...")
        p = Popen(["./phantomjs", "dwm.js", "200", page_url], stdout=PIPE)
        html = p.stdout.read()
        p.wait()
        hutf = html.decode("utf8")
        #c = hutf.split("<!--视频列表区域 -->")[1]
        urls = [(a.text, a['href'])
                for a in SelStr('div.smalList > ul > li > a', hutf)]
        self.align_num = len(str(len(urls)))
        return urls

    def test(self, args):
        url = "http://www.iqiyi.com/v_19rqzugacg.html"
        hutf = self.get_hutf(url)
        tvid = match1(hutf, """param\['tvid'\] = "(\d+)";""")
        vid = match1(hutf, """param\['vid'\] = "([^"]+)";""")
        echo("tvid=", tvid, ", vid=", vid)
        dat = I2().getVMS(tvid, vid)
        for stream in dat['data']['vidl']:
            #if vd == stream["vd"]:
            echo("vd =", stream["vd"])
        return

        url = "http://www.iqiyi.com/playlist521743802.html"
        hutf = self.get_hutf(url)
        echo(hutf)
        els = SelStr("div.site-piclist_pic > a.site-piclist_pic_link", hutf)
        for e in els:
            echo(e['href'])
        return

        #url = "https://www.iqiyi.com/v_19rr04z9is.html"
        #url = 'http://www.iqiyi.com/v_19rrkxmiss.html'
        url = "http://www.iqiyi.com/v_19rqzugacg.html?list=19rrm106om"
        url = "http://www.iqiyi.com/v_19rqztf338.html?list=19rrm106om"

        hutf = self.get_hutf(url)
        echo(hutf)
        #title = SelStr('meta[property=og:title]', hutf)[0]["content"]
        title = SelStr('meta[name=irTitle]', hutf)[0]["content"]
        echo(title)
        return
        i2 = I2()
        #i2.get_hutf(url)
        tvid = "453406400"
        videoid = "778e9e5286f2ca6a94d8b5da0062f978"
        du = i2.getVMS(tvid, videoid)
        #echo(du)
        #hutf = i2.get_hutf(du)
        #echo(hutf)
        #echo(json.loads(hutf))


if __name__ == '__main__':
    #start(IQIYI)
    IQIYI().test("")
